#!usr/bin/env python3

from blockchain import *
import requests

class ClientPeer:

    def __init__(self, neighbors: list= [], host="localhost", port="8000"):
        self.neighbors: list = neighbors
        self.host = host
        self.port = port

    def broadcast_transaction(self, Transaction):
        payload = Transaction.serialize()
        for neighbor in self.neighbors:
            url = self.host + ":" + neighbor + "/send_transaction"
            requests.post(url, data=payload)
    
    def broadcast_block(self, Block):
        payload = Block.serialize()
        for neighbor in self.neighbors:
            url = self.host + ":" + neighbor + "/send_block"
            requests.post(url, data=payload)



