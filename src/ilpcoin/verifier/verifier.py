#!usr/bin/env python3

from ilpcoin.verifier.server import Server
from time import sleep
from ilpcoin.common.blockchain import *
from ilpcoin.common.constants import *
import random
import requests
import logging

class Verifier(Server):

    def __init__(self, id:int, host: str=HOST, port: int=PORT, testing=False):

        self.testing: bool = testing

        self.get_neighbors(id)

        super().__init__(id, self.get_blockchain(), host, port, testing)
        self.start()

        # TODO register with the queue
    
    # get neighbors from queue when initializing 
    def get_neighbors(self, id) -> None:
        if not self.testing:
            r = requests.get(QUEUE_HOST + ":" + str(QUEUE_PORT) + "/get_neighbors")
            self.neighbors = pickle.loads(r.content)
        else:
            self.neighbors: List[int] = [1, 2, 3]
            self.neighbors.remove(id)

    # get blockchain from neighbors when starting up
    def get_blockchain(self) -> Optional[Blockchain]:
        if not self.testing:
            n: int = random.choice(self.neighbors)
            r = requests.get(HOST + ":" + str(PORT + n) + "/get_blockchain")
            logging.debug("Got raw blockchain from neighbors " + str(r.content))
            return Blockchain.deserialize(r.content)
    
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
        
        return response


# TODO
# test with fake blocks for verifier
# test verifier communication
# implement verifier registration
