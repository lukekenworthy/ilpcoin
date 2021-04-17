#!usr/bin/env python3

from pickle import LIST
from typing import Dict, Tuple
from ilpcoin.verifier.server import Server
from time import sleep
from ilpcoin.common.blockchain import *
from ilpcoin.common.constants import *
import requests
import logging
from ilpcoin.common.sample_ilps.knapsack import *
import random

from requests.models import StreamConsumedError

class Verifier(Server):

    # init starts the server as well
    def __init__(self, id:int, host: str=HOST, port: int=PORT, testing=False):

        self.testing: bool = testing

        self.get_neighbors(id)
        b = self.get_blockchain()

        super().__init__(id, self.get_blockchain(), host, port, testing)
        self.start()

        # verifiers after the first should not have empty chains
        while self.id != 1 and self.blockchain.get_len() == 0:
            sleep(1)
            self.blockchain = self.get_blockchain()

        r = requests.get("http://" + QUEUE_HOST + ":" + str(QUEUE_PORT) + "/register_verifier/" + str(self.id))

        self.block_queue: List[Dict] = []

        # genesis block -> only the first verifier should make this
        if self.id == 1:
            ilp = knapsack()
            b = Block([], '', 0, ilp.get_id(), ilp.solve())
            while not b.validate_nonce(HARDNESS):
                b.nonce = random.randrange(0, 1000000)
            self.blockchain.add_block(b)

    
    # get neighbors from queue when initializing 
    def get_neighbors(self, id) -> None:
        if not self.testing:
            r = requests.get("http://" + QUEUE_HOST + ":" + str(QUEUE_PORT) + "/get_neighbors/5")
            self.neighbors = pickle.loads(r.content)
            self.neighbors = [int(el) for el in self.neighbors]
            if id in self.neighbors:
                self.neighbors.remove(id)
            print(self.neighbors)
        else:
            self.neighbors: List[int] = [1, 2]

    # get blockchain from neighbors when starting up
    def get_blockchain(self) -> Optional[Blockchain]:
        if not self.testing:
            longest_chain = -1
            longest_neighbor = 0

            # figure out who has the longest fork
            for i in self.neighbors:
                r = requests.get("http://" + HOST + ":" + str(PORT + int(i)) + "/get_length")
                if int(r.content) > longest_chain:
                    longest_chain = int(r.content)
                    longest_neighbor = i
            
            # grab their chain
            if longest_neighbor == 0:
                return Blockchain([])
            else:
                r = requests.get("http://" + HOST + ":" + str(PORT + longest_neighbor) + "/get_blockchain")
                return Blockchain.deserialize(r.content)
        else:
            return Blockchain(blocks=[])
    
    # advertise a found block to neighbors
    def advertise_block(self, b: Block, sender:int):
        headers = {"Content-Type":"application/binary",}
        if self.testing:
            return 
        for i in self.neighbors:
            if i != sender:
                url = f"http://{HOST}:{PORT + int(i)}/send_block/{self.id}" 
                r = requests.put(url, data=b.serialize(),headers=headers)
                logging.debug(f"Advertised block to {i}")
                # maybe eventually we want to handle failed requests here -> perhaps by updating our view of the chain?

    # verify a block
    def process_new_block(self, b: Block, sender:int) -> str:
        response = SUCCESS

        # validate the transactions in the block
        valid = b.transactions[0].amount < REWARD
        l = self.blockchain.get_len()

        # start from index 1 to skip the mining reward
        # may eventually want to optimize this 
        for i in range(1, len(b.transactions)):
            t = b.transactions[i]
            if not self.blockchain.verify_transaction(t, l, i):
                response = INVALID_TRANSACTION
                break
        
        # validate static components - nonce, previous_hash, proof of work
        if not self.blockchain.get_top():
            logging.debug("top of the chain is None")
        if not b.validate_block(self.blockchain.get_top(), HARDNESS):
            response = INVALID_NONCE_OR_POW
        
        # add this block on the queue of stuff to be advertised
        if response == SUCCESS:
            self.block_queue.append({"block":b, "sender":sender})
            # tell the queue that we verified a solution
            r = requests.get("http://" + QUEUE_HOST + ":" + str(QUEUE_PORT) + "/" + 'verify_ilp/' + str(b.ILP))
        
        return response
    
    # this loop just advertises blocks in the main thread
    # we want advertising to be concurrent to request processing else we risk system wide deadlock
    # eventual optimization: each neighbor gets a thread
    def run(self):
        counter = 0

        while True:
            if self.block_queue != []:
                logging.debug(f"Found block {counter}")
                self.advertise_block(self.block_queue[0]['block'], self.block_queue[0]['sender'])
                self.block_queue.pop(0)
                counter += 1
            else:
                sleep(0.1)


