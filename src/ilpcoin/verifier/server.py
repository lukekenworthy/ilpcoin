#!usr/bin/env python3

from flask import Flask
from ilpcoin.blockchain import Block, Blockchain, Transaction
import threading

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
    
    # should be used by the verifier to reset a blockchain if necessary
    def set_blockchain(self, b:Blockchain):
        self.blockchain = b
    
    def start(self):
        if not self.testing:
            threading.Thread(target=app.run, kwargs={"debug":False, "host":self.host, "port":self.port}).start()

    # used by miners to send a mined block and by verifiers to send a verified block
    @app.route('/send_block', methods=['POST'])
    def get_block():
        try:
            block = Block()
            block.deserialize(request.form['block'])
            self.blocks_to_verify.append(block)
            self.new_block += 1
        except:
            print("Bad Request, no block found")
    
    # eventually will be used to share transactions
    @app.route('/send_transaction', methods=['POST'])
    def get_transaction():
        try:
            transaction = Transaction()
            transaction.deserialize(request.form['transaction'])
            self.transactions_to_verify.append(transaction)
            self.new_transaction += 1
        except:
            print("Bad Request, no transaction found")

    # used for initialization
    @app.route('/get_blockchain', methods=['GET'])
    def give_blockchain(self):
        return self.blockchain.serialize()
    
    # used by miners to get the previous block
    @app.route('/get_previous', methods=['GET'])
    def get_previous(self):
        return self.blockchain.get_top().serialize()
    
    # used by verifiers to check that they're on the right fork
    @app.route('/get_length', methods=['GET'])
    def get_length(self):
        return str(len(self.blockchain))







    