#!usr/bin/env python3

from ilpcoin.common.blockchain import Block, Transaction, Blockchain
from ilpcoin.common.constants import HARDNESS, PORT, QUEUE_HOST, QUEUE_PORT, HOST, REWARD
from ilpcoin.common.ilp import Ilp, IlpSolution
import requests
import random
from typing import List, Optional, Set
import uuid
import pickle
from time import sleep

class InvalidResponseError(Exception):
    pass

class ClientPeer:

    def __init__(self, host="localhost", id:int=0, buggy:bool=False) -> None:
        self.host = host
        self.port:str = str(8000 + id)
        self.id:str = str(id)
        self.reset_neighbors(5)
        self.buggy = buggy # to be used in tests

    def reset_neighbors(self, n) -> None:
        self.neighbors = self.get_n_neighbors(n)
    

    # def gen_transactions(self) -> List[Transaction]:
    #     neighbors_valid = False
    #     neighbor_port = None
    #     r = None
    #     while not neighbors_valid:
    #         neighbor = random.choice(self.neighbors)
    #         neighbor_port = PORT + int(neighbor)
    #         url = f"http://{HOST}:{neighbor_port}/get_blockchain"
    #         r = requests.get(url)

    #         print(f"get_previous status code {r.status_code}")
    #         if r.status_code == 200:
    #             neighbors_valid = True
    #         else:
    #             sleep(1)

    #     blockchain_text = r.content
    #     blockchain: Blockchain = Blockchain().deserialize(blockchain_text)

    #     users: Set[str] = set()
    #     for block in blockchain.blockchain:
    #         for transaction in block.transactions:
    #             users.add(transaction.sender)
    #             users.add(transaction.receiver)

        
        


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
        url = f"http://{QUEUE_HOST}:{QUEUE_PORT}/get_neighbors/{n}"
        r = requests.get(url)
        if r.status_code != 200:
            raise InvalidResponseError("No neighbors found.")
        neighbors = pickle.loads(r.content)
        return neighbors




    def start_mine(self):
        while True:
            r = requests.get(f"http://{QUEUE_HOST}:{QUEUE_PORT}/get_top_ilp")
            ilp_text = r.text
            print(ilp_text)
            ilp = Ilp.deserialize_s(ilp_text) 
            neighbors_valid = False
            neighbor_port = None
            while not neighbors_valid:
                neighbor = random.choice(self.neighbors)
                neighbor_port = PORT + int(neighbor)
                url = f"http://{HOST}:{neighbor_port}/get_previous"
                r = requests.get(url)

                print(f"get_previous status code {r.status_code}")
                if r.status_code == 200:
                    neighbors_valid = True
                sleep(1)

            previous_block_text = r.content
            prev_block: Block = Block().deserialize(previous_block_text)
            prev_ilp_id = prev_block.ILP
            top_ilp_id = ilp.uid
            # print(f"Top ILP has ID {top_ilp_id} and prev block has id {prev_ilp_id}")
            if prev_ilp_id != top_ilp_id - 1:
                continue

            # print("Attempting solve")

            solved_ilp = ilp.solve()
            if solved_ilp is None:
                continue
            
            # print("ILP Solved")

            prev_hash = prev_block.hash()
            mining_reward = Transaction(self.id, self.id, REWARD)
            giveaway: List[Transaction] = []
            for _ in range(REWARD - 1):
                giveaway.append(Transaction(self.id, str(uuid.uuid4()), 1))
            new_block = Block([mining_reward, *giveaway], str(prev_hash))
            new_block.ILP = ilp.get_id()
            new_block.ILP_solution = solved_ilp
            mx = 2 ** 32 - 1
            while True and not self.buggy:
                new_block.nonce = random.randrange(mx)
                if new_block.validate_nonce(HARDNESS):
                    break

            url = f"http://{HOST}:{neighbor_port}/send_block/{self.id}"
            print(f"about to post to {url}")
            headers = {"Content-Type":"application/binary",}
            r = requests.put(url, data=new_block.serialize(),headers=headers)
            #r = requests.post(url, payload)
            print(f"sent a block w code {r.status_code}")
            

        




