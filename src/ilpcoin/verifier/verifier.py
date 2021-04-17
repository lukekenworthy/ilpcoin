#!usr/bin/env python3

from ilpcoin.verifier.server import Server
from time import sleep
from ilpcoin.common.blockchain import *
from ilpcoin.common.constants import *
import requests
import logging
from ilpcoin.common.sample_ilps.knapsack import *

class Verifier(Server):

    # init starts the server as well
    def __init__(self, id:int, host: str=HOST, port: int=PORT, testing=False):

        self.testing: bool = testing

        self.get_neighbors(id)
        b = self.get_blockchain()

        # eventually we may want to allow for dishonest neighbors
        assert(b.verify_blockchain())

        super().__init__(id, self.get_blockchain(), host, port, testing)
        self.start()

        # TODO register with the queue

        self.block_queue: List[Block] = []
    
    # get neighbors from queue when initializing 
    def get_neighbors(self, id) -> None:
        if not self.testing:
            r = requests.get(QUEUE_HOST + ":" + str(QUEUE_PORT) + "/get_neighbors")
            self.neighbors = pickle.loads(r.content)
        else:
            self.neighbors: List[int] = [1, 2]
            self.neighbors.remove(id)

    # get blockchain from neighbors when starting up
    def get_blockchain(self) -> Optional[Blockchain]:
        if not self.testing:
            longest_chain = -1
            longest_neighbor = 0

            # figure out who has the longest fork
            for i in self.neighbors:
                r = requests.get(HOST + ":" + str(PORT + i) + "/get_length")
                if int(r.content) > longest_chain:
                    longest_chain = int(r.content)
                    longest_neighbor = i
            
            # grab their chain
            r = requests.get(HOST + ":" + str(PORT + longest_neighbor) + "/get_blockchain")
            return Blockchain.deserialize(r.content)
        else:
            return Blockchain(blocks=[])
    
    # advertise a found block to neighbors
    def advertise_block(self, b: Block):
        headers = {
        "Content-Type":"application/binary",
        }
        if self.testing:
            for i in self.neighbors:
                url = "http://" + HOST + ":" + str(PORT + i) + "/send_block"
                r = requests.put(url, data=b.serialize(),headers=headers)
                logging.debug(f"Advertised block to {i}")
                # maybe eventually we want to handle failed requests here -> perhaps by updating our view of the chain?

    # verify a block
    def process_new_block(self, b: Block) -> str:
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
        if not b.validate_block(self.blockchain.get_top(), HARDNESS):
            response = INVALID_NONCE_OR_POW
        
        # add this block on the queue of stuff to be advertised
        if response == SUCCESS:
            self.block_queue.append(b)
        
        return response
    
    # this loop just advertises blocks in the main thread
    # we want advertising to be concurrent to request processing else we risk system wide deadlock
    # eventual optimization: each neighbor gets a thread
    def run(self):
        counter = 0

        while True:
            if self.block_queue != []:
                logging.debug(f"Found block {counter}")
                self.advertise_block(self.block_queue[0])
                self.block_queue.pop(0)
                counter += 1
            else:
                sleep(0.1)



# TODO
# implement verifier registration
