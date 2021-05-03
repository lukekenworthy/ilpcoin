from typing import List, Set
from flask import Flask, request
import requests
from ilpcoin.common.ilp import *
from ilpcoin.common.constants import *
import ilpcoin.common.constants
from ilpcoin.common.sample_ilps.random_knapsack import random_knapsack
import queue
import logging
import threading
from random import sample

# IlpQueue represents a queue of ilps. 
# This state needs to be written to databases. 
class IlpQueue:
    def __init__(self, initial_verifiers : List[int] = [], generate_random_ilps = True):
        self.q = queue.Queue() # the queue 
        self.top : Optional[Ilp] = None  # the top ilp, currently worked on by miners
        self.count : int = 0   # the number of verifiers who have provided solutions for self.top
        self.ilp_history : dict[int, Ilp] = {} # a dictionary mapping all previous ilp IDs to their ilp problems. 
        self.last_used_uid = 0 # last uid; let's not repeat uids!   
        self.verifiers = initial_verifiers
        self.last_used_verifier = 0
        self.generate_random_ilps = generate_random_ilps
        if self.generate_random_ilps: 
            self.__add_random_ilp()

    # Add an Ilp (see ilp.py for representation) to the back of the queue
    def add(self, ilp : Ilp) -> int:
        self.last_used_uid += 1
        ilp.set_id(self.last_used_uid)
        self.q.put(ilp)
        self.ilp_history[ilp.get_id()] = ilp
        if not self.top: 
            self.top = self.q.get()
            logging.debug(f"Top ILP has ID {self.top.get_id()}")
        return ilp.get_id()
    
    # Return a verifier ip, different from the last time
    def get_verifier_ip(self) -> Optional[int]: 
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
    
    def __add_random_ilp(self): 
        self.add(random_knapsack())

    def __complete_item(self) -> None:
        logging.debug("Ilp with id " + str(self.top.get_id()) + " is popped from queue.") 

        if not self.q.empty():
            self.top = self.q.get()
        else:
            if self.generate_random_ilps: 
                self.__add_random_ilp()
                self.top = self.q.get()
            else: 
                self.top = None

        self.count = 0

    # Called when a solution has come in for the current Ilp to increment count, 
    # and move to the next item in the queue if need be. 
    def incr_count(self, uid : int) -> bool:
        if not self.get_top():
            return False

        if (self.get_top().get_id() != int(uid)):
            logging.debug(f"Verifying ILP w ID {uid} but top of the queue is {self.get_top().get_id()}")
            return False

        self.count += 1
        if(self.count >= ilpcoin.common.constants.VERIFIERS_NEEDED):
            self.__complete_item()
        logging.debug(f"Registering solution for ilp with id {uid}")
        return True


ilp_queue = IlpQueue(generate_random_ilps=True)

app = Flask(__name__)

# Will return the new UID
@app.route('/add_ilp', methods=['POST'])
def add_ilp():
    new_ilp_serialized : str = request.form['ilp']
    if not new_ilp_serialized:
        return FAILURE
    new_ilp = Ilp.deserialize_s(new_ilp_serialized)
    ilp_queue.add(new_ilp)
    logging.debug(f"Added new ilp with ID {new_ilp.get_id()}")

    return str(new_ilp.get_id())

@app.route('/get_top_ilp', methods=['GET'])
def get_top_ilp():
    result = ilp_queue.get_top()
    return result.serialize_s() if result else ILP_NOT_FOUND

@app.route('/get_ilp_by_id/<uid>', methods=['GET'])
def get_ilp_by_id(uid):
    logging.debug("Looking up ilp with id: " + uid)
    result = ilp_queue.lookup_ilp(int(uid))
    return result.serialize_s() if result else ILP_NOT_FOUND

# will return
@app.route('/get_solution_by_id/<uid>', methods=['GET'])
def get_solution_by_id(uid, tries : int = 3):
    for i in range(tries): 
        id = ilp_queue.get_verifier_ip()
        if not id: 
            return NO_VERIFIERS
        r = requests.get("http://" + (HOST + ":" + str(int(PORT) + int(id))) + "/get_ilp_solution/" + str(uid), timeout=3)
        if r.text: 
            return r.text
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
    logging.debug(f"sending neighbors {res}")
    return pickle.dumps(res)