#!usr/bin/env python3

from flask import Flask
from ilpcoin.common.blockchain import Block, Blockchain, Transaction
import threading
import logging

app = Flask(__name__)

class Server:

    def __init__(self, id: int, b: Blockchain, host: str="localhost",
        port: int=8000, testing: bool=False):
        self.id: int = id
        self.host: str = host
        self.port: str = str(port+id)
        self.testing: bool = testing

        self.blockchain = b

        # collection of unverified transactions
        self.transactions_to_verify: list = []
        self.new_transaction: int = 0

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

    # used by miners to send a mined block and by verifiers to send a verified block
    @app.route('/send_block', methods=['POST'])
    def get_block():
        try:
            block = Block().deserialize(request.form['block'])
            self.blocks_to_verify.append(block)
            self.new_block += 1

            logging.debug("Got block " + request.form['block'])
        except:
            logging.warn("Bad Request, no block found")

    # eventually will be used to share transactions
    @app.route('/send_transaction', methods=['POST'])
    def get_transaction():
        try:
            transaction = Transaction().deserialize(request.form['transaction'])
            self.transactions_to_verify.append(transaction)
            self.new_transaction += 1
            logging.debug("Got transaction " + request.form['transaction'])
        except:
            logging.warn("Bad Request, no transaction found")

    # used for initialization
    @app.route('/get_blockchain', methods=['GET'])
    def give_blockchain(self):
        logging.debug("Giving blockchain " + self.blockchain.serialize())
        return self.blockchain.serialize()

    # used by miners to get the previous block
    @app.route('/get_previous', methods=['GET'])
    def get_previous(self):
        logging.debug("Giving previous " + self.blockchain.get_top().serialize())
        return self.blockchain.get_top().serialize()

    # used by verifiers to check that they're on the right fork
    @app.route('/get_length', methods=['GET'])
    def get_length(self):
        logging.debug("Giving length " + str(len(self.blockchain)))
        return str(len(self.blockchain))







