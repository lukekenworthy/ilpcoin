#!usr/bin/env python3

from typing import Optional
from flask import Flask, request
from ilpcoin.common.blockchain import Block, Blockchain, Transaction
import threading
import logging
from ilpcoin.common.constants import BLOCKSIZE
from ilpcoin.verifier.__main__ import verifier

app = Flask(__name__)

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

        logging.debug("Initializing server host {host} port {self.port} id {self.id} testing {self.testing}")

    # should be used by the verifier to reset a blockchain if necessary
    def set_blockchain(self, b:Blockchain):
        self.blockchain = b

    def start(self):
        if not self.testing:
            logging.debug("Starting server")
            threading.Thread(target=app.run, kwargs={"debug":False, "host":self.host, "port":self.port}).start()
        else:
            logging.debug("Test mode suppressing server")

app = Flask(__name__)

# used by miners to send a mined block and by verifiers to send a verified block
@app.route('/send_block', methods=['POST'])
def get_block():
    block = Block().deserialize(request.form['block'])
    verifier.blocks_to_verify.append(block)
    verifier.new_block += 1
    logging.debug("Got block " + request.form['block'])
    return 'TODO'

# used for initialization
@app.route('/get_blockchain', methods=['GET'])
def give_blockchain():
    logging.debug("Giving blockchain " + str(verifier.blockchain.serialize()))
    return verifier.blockchain.serialize()

# used by miners to get the previous block
@app.route('/get_previous', methods=['GET'])
def get_previous():
    logging.debug("Giving previous " + str(verifier.blockchain.get_top().serialize()))
    return verifier.blockchain.get_top().serialize()

# used by verifiers to check that they're on the right fork
@app.route('/get_length', methods=['GET'])
def get_length(self):
    logging.debug("Giving length " + str(verifier.blockchain.get_len()))
    return str(verifier.blockchain.get_len())

@app.route('/get_value_by_user/<username>', methods=['GET'])
def get_value_by_user(username):
    l = verifier.blockchain.get_len()
    return str(verifier.blockchain.get_value_by_user(username, l, BLOCKSIZE))

@app.route('/get_ilp_solution/<id>', methods=['GET'])
def get_ilp_solution(id):
    l = verifier.blockchain.get_solution_by_id(id)
    if l: 
        return l.serialize() 
    else: 
        return '2: Not found' 




