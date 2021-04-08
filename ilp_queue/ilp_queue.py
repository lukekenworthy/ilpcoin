from flask import Flask
from ilp import *
import queue
import threading

# how many verifiers required to pop the top of the queue
VERIFIERS_REQUIRED = 3



# ToDo: All the database stuff
# ToDo: The "DNS" service that can find neighbors
# ToDo: Authentication
# ToDo: Input sanitization
# ToDo

class IlpQueue:
    def __init__(self):
        self.q = queue.Queue()
        self.top : Ilp = None
        self.count : int = 0
        self.ilp_history : dict[int, Ilp] = {}
        self.soln_history : dict[int, IlpSolution] = {}
        self.last_used_uid = 0

    @classmethod
    def resume_from_database(cls) -> 'IlpQueue':
        #ToDo
        return cls()

    def add(self, ilp : Ilp) -> int:
        last_used_uid += 1
        ilp.setId(last_used_uid)
        self.q.put(ilp)
        return ilp.getId()

    def get_top(self) -> Ilp:
        return self.top

    def lookup_ilp(self, id : int) -> Ilp:
        # do we want to query a verifier here?
        try:
            return ilp_history[id]
        except:
            return None

    def lookup_solution(self, id : int)  -> IlpSolutionp:
        # do we want to query a verifier here?
        # how do we get these, anyway?
        try:
            return soln_history[id]
        except:
            return None

    def __complete_item(self) -> None:
        if not q.empty():
            self.top = self.q.get()
        else:
            self.top = None
        self.count = 0

    def incr_count(self, uid : int) -> bool:
        if not self.get_top():
            return False

        if (self.get_top().getId() != uid):
            return False

        self.count += 1
        if(self.count >= VERIFIERS_REQUIRED):
            self.__complete_item()
        return True


ilp_queue = IlpQueue.resume_from_database()

app = Flask(__name__)

# Will return the new UID
@app.route('/add_ilp', methods=['POST'])
def add_ilp(new_ilp):
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
    return str(ilp_queue.incr_count())

@app.route('/get_neighbors/<n>', methods=['GET']):
def get_neighbors(n):
    # todo
    pass


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
