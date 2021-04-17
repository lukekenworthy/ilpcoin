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

    def __init__(self, id: int, b: Optional[Blockchain], host: str="localhost",
        port: int=8000, testing: bool=False):
        self.id: int = id
        self.host: str = host
        self.port: str = str(port+id)
        self.testing: bool = testing

        self.blockchain = b

        # collection of unverified blocks
        self.blocks_to_verify = []
        self.new_block: int = 0

        logging.debug(f"Initializing server host {host} port {self.port} id {self.id} testing {self.testing}")

    # should be used by the verifier to reset a blockchain if necessary
    def set_blockchain(self, b:Blockchain):
        self.blockchain = b

    def start(self):
        logging.debug("Starting server")
        threading.Thread(target=app.run, kwargs={"debug":False, "host":self.host, "port":self.port, "threaded":True}).start()

app = Flask(__name__)

# used by miners to send a mined block and by verifiers to send a verified block
# this block should be the top of the blockchain
@app.route('/send_block/<sender>', methods=['POST', 'PUT'])
def get_block(sender) -> str:
    block: Block = Block.deserialize(request.get_data())
    r = main.verifier.process_new_block(block, int(sender))
    logging.debug(f"Processed block and responded {r}")
    return r

# used for initialization
@app.route('/get_blockchain', methods=['GET'])
def give_blockchain():
    logging.debug("Giving blockchain " + str(main.verifier.blockchain.serialize()))
    return main.verifier.blockchain.serialize()

# used by miners to get the previous block
@app.route('/get_previous', methods=['GET'])
def get_previous():
    b = main.verifier.blockchain.get_top()
    if not b:
        return EMPTY_CHAIN
    logging.debug("Giving previous")
    return b.serialize()

# used by verifiers to check that they're on the right fork
@app.route('/get_length', methods=['GET'])
def get_length():
    logging.debug("Giving length " + str(main.verifier.blockchain.get_len()))
    return str(main.verifier.blockchain.get_len())

@app.route('/get_value_by_user/<username>', methods=['GET'])
def get_value_by_user(username):
    l = main.verifier.blockchain.get_len()
    return str(main.verifier.blockchain.get_value_by_user(username, l, BLOCKSIZE))

@app.route('/get_ilp_solution/<id>', methods=['GET'])
def get_ilp_solution(id):
    l = main.verifier.blockchain.get_solution_by_id(id)
    if l: 
        return l.serialize() 
    else: 
        return ILP_NOT_FOUND 




