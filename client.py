#!usr/bin/env python3

from flask import Flask
from blockchain import *

app = Flask(__name__)

class ServerPeer:

    def __init__(self, id, block_size):
        self.id: int = id
        self.block_size: int = block_size
        self.transactions = []
        self.blockchain = []
    
    @app.route('/send_block', methods=['POST'])
    def get_block():
        try:
            block = request.form['block']
            # idk deserialize and validate the block
            print(block)
        except:
            print("Bad Request, no block found")
    
    @app.route('/send_transaction', methods=['POST'])
    def get_transaction():
        try:
            transaction = request.form['transaction']
            print(transaction)
        except:
            print("Bad Request, no transaction found")







    