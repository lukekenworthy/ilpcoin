#!usr/bin/env python3

from pickle import bytes_types
from typing import Optional
from flask import Flask, request
from ilpcoin.common.blockchain import Block, Blockchain, Transaction
import threading
import logging
from ilpcoin.common.constants import *
import ilpcoin.verifier.__main__ as main

class Server:

    '''
    The server class represents a basic participant in the blockchain. It can be extended by purpose-specific members of the chain, such as verifiers. 

    A server has an id on the network, an associated version of the blockchain, and exposes various endpoints for other participants to interact with it. 

    Attributes
    ----------
    id : int
        The id of this verifier. Globally unique. 
    host : str
        The ip where this verifier is hosted. Defaults to 'localhost'
    port : int
        The port where this verifier is hosted. 
    testing : bool 
        Testing mode enabled? Set to false unless working with the unit testing suite. 
    blockchain : Blockchain 
        This server's view of the blockchain
    blocks_to_verify : List[Block]
        The set of blocks that have not yet been verified
    """
    
    '''
    def __init__(self, id: int, b: Optional[Blockchain], host: str="localhost",
        port: int=8000, testing: bool=False):
        '''Initialize a new verifier.'''
        self.id: int = id
        self.host: str = host
        self.port: str = str(port+id)
        self.testing: bool = testing

        self.blockchain = b

        # collection of unverified blocks
        self.blocks_to_verify = []
        self.new_block: int = 0

        logging.debug(f"Initializing server host {host} port {self.port} id {self.id} testing {self.testing}")

    def set_blockchain(self, b:Blockchain):
        '''Reset the blockchain representation if necessary.'''
        self.blockchain = b

    def start(self):
        '''Start the server on a new thread.'''
        logging.debug("Starting server")
        threading.Thread(target=app.run, kwargs={"debug":False, "host":self.host, "port":self.port, "threaded":True}).start()

app = Flask(__name__)

@app.route('/send_block/<sender>', methods=['POST', 'PUT'])
def get_block(sender) -> str:
    '''Receive and process a serialized block
    
    Miners use this to send mined blocks and verifiers use it to send verified blocks. 
    The block sent should always be the top of the blockchain.
    '''

    block: Block = Block.deserialize(request.get_data())
    r = main.verifier.process_new_block(block, int(sender))
    logging.debug(f"Processed block and responded {r}")
    return r

@app.route('/get_blockchain', methods=['GET'])
def give_blockchain():
    '''Return a serialized copy of the entire blockchain. 
    
    This is used by other verifiers on initialization to discover the current state 
    of the blockchain. 
    '''
    logging.debug("Giving blockchain " + str(main.verifier.blockchain.serialize()))
    return main.verifier.blockchain.serialize()

@app.route('/get_previous', methods=['GET'])
def get_previous():
    '''
    Return the previous block serialized, which miners need to hash and insert into subsequent blocks.
    '''
    b = main.verifier.blockchain.get_top()
    if not b:
        return EMPTY_CHAIN
    logging.debug("Giving previous")
    return b.serialize()

@app.route('/get_length', methods=['GET'])
def get_length():
    '''Returns the number of blocks in this server's version of the blockchain. 
    
    Used by other verifiers to determine if they're on the correct fork. 
    '''
    logging.debug("Giving length " + str(main.verifier.blockchain.get_len()))
    return str(main.verifier.blockchain.get_len())

@app.route('/get_value_by_user/<username>', methods=['GET'])
def get_value_by_user(username):
    '''Query the blockchain to find out the current balance of `username`'s account. 
    
    In current implementation, will replay the entire blockchain.'''
    l = main.verifier.blockchain.get_len()
    return str(main.verifier.blockchain.get_value_by_user(username, l, BLOCKSIZE))

@app.route('/get_ilp_solution/<id>', methods=['GET'])
def get_ilp_solution(id):
    '''Query the blockchain for solution with id `id`. 
    
    Used by the queue to return solutions to customers.
    '''
    l = main.verifier.blockchain.get_solution_by_id(id)
    if l: 
        return l.serialize_s() 
    else: 
        return ILP_NOT_FOUND 




