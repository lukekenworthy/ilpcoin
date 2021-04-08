from flask import Flask
from ilp import *
import threading

VERIFIERS_REQUIRED = 3

app = Flask(__name__)


# Will return the new UID
@app.route('/add_ilp/<new_ilp>', methods=['POST'])
def add_ilp(new_ilp):
    pass

# will return
@app.route('/get_solved_ilp/<uid>', methods=['POST'])
def get_solved_ilp(uid):
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
