#!usr/bin/env python3

from ilpcoin.common.blockchain import Block, Transaction
from ilpcoin.common.ilp import Ilp, IlpSolution
import requests
import random
from typing import List, Optional
import uuid

class InvalidResponseError(Exception):
    pass

class ClientPeer:

    def __init__(self, host="localhost", id:int=0) -> None:
        self.host = host
        self.port:str = str(8000 + id)
        self.id:str = str(id)
        self.reset_neighbors(5)

    def reset_neighbors(self, n) -> None:
        self.neighbors = self.get_n_neighbors(n)

    """
    def broadcast_transaction(self, Transaction):
        payload = Transaction.serialize()
        for neighbor in self.neighbors:
            url = self.host + ":" + str(neighbor) + "/send_transaction"
            requests.post(url, data=payload)
    
    def broadcast_block(self, Block):
        payload = Block.serialize()
        for neighbor in self.neighbors:
            url = self.host + ":" + neighbor + "/send_block"
            requests.post(url, data=payload)
    """

    def get_n_neighbors(self, n:int) -> List[str]:
        url = f"{self.host}:{self.port}/get_neighbors/{n}"
        r = requests.get(url)
        if r.status_code != 200:
            raise InvalidResponseError("No neighbors found.")
        neighbors = r.json()
        return neighbors["neighbors"]




    def start_mine(self):
        while True:
            r = requests.get(f"{self.host}:{self.port}/get_top_ilp")
            ilp_text = r.text
            ilp = Ilp.deserialize(ilp_text.encode("ascii")) 

            neighbors_valid = False
            while not neighbors_valid:
                neighbor = random.choice(self.neighbors)
                url = f"{self.host}:{neighbor}/get_previous"
                r = requests.get(url)
                if r.status_code == 200:
                    neighbors_valid = True

            previous_block_text = r.content
            prev_block: Block = Block().deserialize(previous_block_text)
            prev_ilp_id = prev_block.ilp.uid
            top_ilp_id = ilp.uid
            if prev_ilp_id == top_ilp_id - 1:
                continue

            solved_ilp = ilp.solve()
            if solved_ilp is None:
                continue
            
            prev_hash = prev_block.hash()
            transaction = Transaction(self.id, self.id, 5)
            new_block = Block([transaction], str(prev_hash))
            new_block.ILP = ilp.get_id()
            new_block.ILP_solution = solved_ilp
            mx = 2 ** 32 - 1
            while True:
                new_block.nonce = random.randrange(mx)
                if new_block.validate_nonce(10):
                    break

            url = f"{self.host}:{self.port}/send_block"
            payload = {
                "block": new_block.serialize()
            }
            r = requests.post(url, payload)
            

        




