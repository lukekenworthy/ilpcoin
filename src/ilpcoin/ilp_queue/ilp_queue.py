from typing import List, Set
from flask import Flask, request
import requests
from ilpcoin.common.ilp import *
from ilpcoin.common.constants import *
import queue
import logging
import threading
from random import sample

# how many verifiers required to pop the top of the queue
VERIFIERS_REQUIRED = 3

# ToDo: All the database stuff
# ToDo: Authentication
# ToDo: Input sanitization

# IlpQueue represents a queue of ilps. 
# This state needs to be written to databases. 
class IlpQueue:
    def __init__(self, initial_verifiers : List[str] = []):
        self.q = queue.Queue() # the queue 
        self.top : Optional[Ilp] = None  # the top ilp, currently worked on by miners
        self.count : int = 0   # the number of verifiers who have provided solutions for self.top
        self.ilp_history : dict[int, Ilp] = {} # a dictionary mapping all previous ilp IDs to their ilp problems. 
        # self.soln_history : dict[int, IlpSolution] = {} #  a dictionary mapping all previous solved ilp IDs to their solutions. Right now, this is never updated
        self.last_used_uid = 0 # last uid; let's not repeat uids!   
        self.verifiers = initial_verifiers
        self.last_used_verifier = 0

    # Eventually, this will query a database and reconstruct the Ilp from there
    @classmethod
    def resume_from_database(cls) -> 'IlpQueue':
        #ToDo
        return cls()

    # Add an Ilp (see ilp.py for representation) to the back of the queue
    def add(self, ilp : Ilp) -> int:
        self.last_used_uid += 1
        ilp.set_id(self.last_used_uid)
        self.q.put(ilp)
        self.ilp_history[ilp.get_id()] = ilp
        if not self.top: 
            self.top = self.q.get()
        return ilp.get_id()
    
    # Return a verifier ip, different from the last time
    def get_verifier_ip(self): 
        if not self.verifiers: 
            return None
        self.last_used_verifier += 1
        return self.verifiers[self.last_used_verifier % len(self.verifiers)]

    def add_verifer(self, ip): 
        self.verifiers.append(ip)

    # Return the current ilp to work on
    def get_top(self) -> Optional[Ilp]:
        return self.top

    # Get historical ilp
    def lookup_ilp(self, id : int) -> Optional[Ilp]:
        # do we want to query a verifier here?
        try:
            return self.ilp_history[id]
        except:
            return None

    # def lookup_solution(self, id : int)  -> Optional[IlpSolution]:
    #     # do we want to query a verifier here?
    #     # how do we get these, anyway?
    #     try:
    #         return self.soln_history[id]
    #     except:
    #         return None

    def __complete_item(self) -> None:
        print("Ilp with id " + str(self.top.get_id()) + " is popped from queue.") 
        if not self.q.empty():
            self.top = self.q.get()
        else:
            self.top = None
        self.count = 0

    # Called when a solution has come in for the current Ilp to increment count, 
    # and move to the next item in the queue if need be. 
    def incr_count(self, uid : int) -> bool:
        if not self.get_top():
            return False

        if (self.get_top().get_id() != uid):
            return False

        self.count += 1
        if(self.count >= VERIFIERS_REQUIRED):
            self.__complete_item()
        return True


ilp_queue = IlpQueue.resume_from_database()

app = Flask(__name__)

# Will return the new UID
@app.route('/add_ilp', methods=['POST'])
def add_ilp():
    new_ilp_serialized : str = request.form['ilp']
    if not new_ilp_serialized:
        return FAILURE
    new_ilp = Ilp.deserialize_s(new_ilp_serialized)
    ilp_queue.add(new_ilp)
    return str(new_ilp.get_id())

@app.route('/get_top_ilp', methods=['GET'])
def get_top_ilp():
    result = ilp_queue.get_top()
    return result.serialize_s() if result else ILP_NOT_FOUND

@app.route('/get_ilp_by_id/<uid>', methods=['GET'])
def get_ilp_by_id(uid):
    print("Looking up ilp with id: " + uid)
    result = ilp_queue.lookup_ilp(int(uid))
    return result.serialize_s() if result else ILP_NOT_FOUND

# will return
@app.route('/get_solution_by_id/<uid>', methods=['GET'])
def get_solution_by_id(uid, tries : int = 3):
    for i in range(tries): 
        if not ilp_queue.get_verifier_ip(): 
            return NO_VERIFIERS

        r = requests.get(ilp_queue.get_verifier_ip() + "/get_neighbors/" + str(uid), timeout=3)
        if r.content: 
            return r.content
    return TIMEOUT

# Announce to the queue that you have verified a solution for 
# ilp_id
@app.route('/verify_ilp/<ilp_id>', methods=['GET'])
def verify_ilp(ilp_id):
    return SUCCESS if ilp_queue.incr_count(ilp_id) else NOT_TOP_ILP

# add a verifier to the list
@app.route('/register_verifier/<address>', methods=['GET'])
def register_verifier(address): 
    if not address in ilp_queue.verifiers: 
        ilp_queue.add_verifer(address)
    return SUCCESS

# Return n verifier IPs, or all the verifiers if < n
@app.route('/get_neighbors/<n>', methods=['GET'])
def get_neighbors(n):
    try: 
        res = sample(ilp_queue.verifiers, n)
    except: 
        res = ilp_queue.verifiers

    return pickle.dumps(res)