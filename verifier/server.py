#!usr/bin/env python3

from flask import Flask
from blockchain import *
import threading

app = Flask(__name__)

class ServerPeer:

    def __init__(self, id, host="localhost", port="8000", testing=False):
        self.id: int = id
        self.host: str = host
        self.port: str = port+str(id)
        self.testing: bool = testing
    
    def run(self):
        if not self.testing:
            threading.Thread(target=app.run, kwargs={"debug":False, "host":self.host, "port":self.port}).start()

    @app.route('/send_block', methods=['POST'])
    def get_block():
        try:
            block = Block()
            block.deserialize(request.form['block'])
            # idk validate the block
            print(block)
        except:
            print("Bad Request, no block found")
    
    @app.route('/send_transaction', methods=['POST'])
    def get_transaction():
        try:
            transaction = Transaction()
            transaction.deserialize(request.form['transaction'])
            print(transaction)
        except:
            print("Bad Request, no transaction found")







    