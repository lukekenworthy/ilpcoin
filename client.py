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
    
    @app.route('/send_block', methods=['POST')
    def get_block():
        try:
            request.form['block']
    
    @app.route('/send_transaction', methods=['POST'])
    def get_transaction():
        pass







    