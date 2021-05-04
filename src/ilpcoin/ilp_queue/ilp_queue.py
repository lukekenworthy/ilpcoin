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

class IlpQueue:
    '''IlpQueue represents the state for a queue of Ilps. 
    
    The ilp-queue application is backed by this data structure.

    Attributes
    ----------
    q : queue.Queue
        The underlying Python queue that stores the Ilps. 
    top : Optional[Ilp]
        The current Ilp at the head of the queue. This is the Ilp currently being solved 
        by the blockchain.
    count : int
        The number of verifiers who report having solved `top`. 
    ilp_history : dict[int, Ilp]
        A dictionary of every Ilp that has ever been on the queue, indexed by their uid.
    last_used_uid : int
        The most recently assigned uid. ID's are not reused, and this is incremented after each new id is provisioned. 
    verifiers : List[int]
        The set of verifiers that the queue knows about. Verifiers register with the queue on initialization.
    generate_random_ilps : bool
        Set to true if the queue should generate random Ilps to ensure there is always an Ilp available. In
        general, this is set to true, but we switch it to false for deterministic unit testing.
    '''

    def __init__(self, initial_verifiers : List[int] = [], generate_random_ilps = True):
        '''Initializes a new IlpQueue.
        
        In the future, this could be written to a database frequently, and restored from the database 
        on startup.
        '''
        self.q = queue.Queue() 
        self.top : Optional[Ilp] = None 
        self.count : int = 0   
        self.ilp_history : dict[int, Ilp] = {} 
        self.last_used_uid = 0 
        self.verifiers = initial_verifiers
        self._last_used_verifier = 0 # used the ensure different subsets of verifiers are given when queue is used as a DNS
        self.generate_random_ilps = generate_random_ilps
        if self.generate_random_ilps: 
            self.__add_random_ilp()

    def add(self, ilp : Ilp) -> int:
        '''Add an Ilp (see `Ilp`for representation) to the back of the queue.'''
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
        '''Return the id of a ranndom verifier known to be on the network. 
        
        Cycles through verifiers to avoid repetition.
        '''
        
        if not self.verifiers: 
            return None

        self._last_used_verifier += 1

        return self.verifiers[self._last_used_verifier % len(self.verifiers)]

    def add_verifer(self, ip): 
        '''Make the queue aware of a new verifier, with address `ip`'''
        self.verifiers.append(ip)

    def get_top(self) -> Optional[Ilp]:
        '''Return the Ilp the blockchain is currently working on. None otherwise.'''
        return self.top

    def lookup_ilp(self, id : int) -> Optional[Ilp]:
        '''Return the ilp matching `id`.'''
        try:
            return self.ilp_history[id]
        except:
            return None
    
    # Add a random Ilp to the queue
    def __add_random_ilp(self): 
        self.add(random_knapsack(ilpcoin.common.constants.ILP_HARDNESS))

    # Increment the queue to the next element; called when enough verifiers have 
    # checked the solution. 
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

    def incr_count(self, uid : int) -> bool:
        '''Called when a verifier tells the queue that it has solved the top ilp. 
        
        Increments count, and cycles to next Ilp if necessary. 
        '''
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


# The main ilp_queue, that backs the Flask application below.
ilp_queue = IlpQueue(generate_random_ilps=True)

# The queue application. 
app = Flask(__name__)

@app.route('/add_ilp', methods=['POST'])
def add_ilp():
    '''Add the serialized Ilp passed through the request form (encoded as a hexidecimal string).
    
    Returns the ID of the new Ilp.
    '''
    new_ilp_serialized : str = request.form['ilp']
    if not new_ilp_serialized:
        return FAILURE

    new_ilp = Ilp.deserialize_s(new_ilp_serialized)
    ilp_queue.add(new_ilp)

    logging.debug(f"Added new ilp with ID {new_ilp.get_id()}")
    return str(new_ilp.get_id())

@app.route('/get_top_ilp', methods=['GET'])
def get_top_ilp():
    '''Return a hex string serialized Ilp on the top of the queue, if available.
    
    Returns ILP_NOT_FOUND on failure.'''
    result = ilp_queue.get_top()
    return result.serialize_s() if result else ILP_NOT_FOUND

@app.route('/get_ilp_by_id/<uid>', methods=['GET'])
def get_ilp_by_id(uid):
    '''Return a hex string serialization if the Ilp with id `uid`'''
    logging.debug("Looking up ilp with id: " + uid)
    result = ilp_queue.lookup_ilp(int(uid))
    return result.serialize_s() if result else ILP_NOT_FOUND

@app.route('/get_solution_by_id/<uid>', methods=['GET'])
def get_solution_by_id(uid, tries : int = 3):
    ''' Try `tries` times to query random verifiers for a solution to Ilp with id `uid`'''
    for i in range(tries): 
        id = ilp_queue.get_verifier_ip()
        if not id: 
            return NO_VERIFIERS
        r = requests.get("http://" + (HOST + ":" + str(int(PORT) + int(id))) + "/get_ilp_solution/" + str(uid), timeout=3)
        if r.text: 
            return r.text
    return TIMEOUT

@app.route('/verify_ilp/<ilp_id>', methods=['GET'])
def verify_ilp(ilp_id):
    '''Announce to the queue that you have verified a solution for ilp_id.'''
    return SUCCESS if ilp_queue.incr_count(ilp_id) else NOT_TOP_ILP

@app.route('/register_verifier/<address>', methods=['GET'])
def register_verifier(address): 
    '''Announce to the queue that verifier at `address` is online'''
    if not address in ilp_queue.verifiers: 
        ilp_queue.add_verifer(address)
    return SUCCESS

@app.route('/get_neighbors/<n>', methods=['GET'])
def get_neighbors(n):
    '''Returns a pickled list of n verifier IDs that the queue know about. If 
    fewer than n verifiers are known, returns all verifiers.
    '''
    try: 
        res = sample(ilp_queue.verifiers, n)
    except: 
        res = ilp_queue.verifiers
    logging.debug(f"sending neighbors {res}")
    return pickle.dumps(res)