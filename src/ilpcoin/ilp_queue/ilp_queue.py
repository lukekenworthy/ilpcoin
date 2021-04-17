from flask import Flask
from ilpcoin.common.ilp import *
import queue
import threading

# how many verifiers required to pop the top of the queue
VERIFIERS_REQUIRED = 3

# ToDo: All the database stuff
# ToDo: The "DNS" service that can find neighbors
# ToDo: Authentication
# ToDo: Input sanitization
# ToDo

# IlpQueue represents a queue of ilps. 
# This state needs to be written to databases. 
class IlpQueue:
    def __init__(self):
        self.q = queue.Queue() # the queue 
        self.top : Optional[Ilp] = None  # the top ilp, currently worked on by miners
        self.count : int = 0   # the number of verifiers who have provided solutions for self.top
        self.ilp_history : dict[int, Ilp] = {} # a dictionary mapping all previous ilp IDs to their ilp problems. 
        self.soln_history : dict[int, IlpSolution] = {} #  a dictionary mapping all previous solved ilp IDs to their solutions. Right now, this is never updated
        self.last_used_uid = 0 # last uid; let's not repeat uids!   

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
        return ilp.get_id()

    # Return the current ilp to work on
    def get_top(self) -> Optional[Ilp]:
        return self.top

    # ToDo
    def lookup_ilp(self, id : int) -> Optional[Ilp]:
        # do we want to query a verifier here?
        try:
            return self.ilp_history[id]
        except:
            return None

    def lookup_solution(self, id : int)  -> Optional[IlpSolution]:
        # do we want to query a verifier here?
        # how do we get these, anyway?
        try:
            return self.soln_history[id]
        except:
            return None

    def __complete_item(self) -> None:
        if not q.empty():
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
    new_ilp_serialized = request.form.get('ilp')
    new_ilp = Ilp.deserialize(new_ilp_serialized)
    ilp_queue.add(new_ilp)
    return "Confirmed"

@app.route('/get_top_ilp', methods=['GET'])
def get_top_ilp():
    result = ilp_queue.get_top()
    return result.serialize() if result else ""

@app.route('/get_ilp_by_id/<uid>', methods=['GET'])
def get_ilp_by_id(uid):
    result = ilp_queue.lookup_ilp(uid)
    return result.serialize() if result else ""

# will return
@app.route('/get_solution_by_id/<uid>', methods=['GET'])
def get_solution_by_id(uid):
    result = ilp_queue.lookup_solution(uid)
    return result.serialize() if result else "Unsolved"

@app.route('/verify_ilp/<uid>', methods=['GET'])
def verify_ilp(uid):
    return "true" if ilp_queue.incr_count(uid) else "False"

@app.route('/register_verifier/<uid>', methods=['GET'])
def register_verifier(uid): 
    pass
    # oh hallo I am a new verifier todo 

@app.route('/get_neighbors/<n>', methods=['GET'])
def get_neighbors(n):
    pass
    # todo
    # queue can yeet off verifiers that it hasn't heard from 

# @param VERIFIERS_REQUIRED

# For customers:
# /add_ilp(the_ilp)
# /get_solved_ilp(id) → Solution; raises error if not yet solved

# For miners:
# 	/get_top_ilp() → ILP

# For verifiers:
# 	/get_ilp_by_id(id) → ILP
# 	/verification(id) →  bool for whether its top; queue increments its verified count
# 	/give_neighbors(n) → list of random subset of n verifiers
