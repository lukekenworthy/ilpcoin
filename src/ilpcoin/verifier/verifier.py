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
        # hardcoded for now - eventually we will ask the queue for these
        self.neighbors: List[int] = [1, 2, 3]
        self.neighbors.remove(id)

        self.testing: bool = testing

        super().__init__(id, self.get_blockchain(), host, port, testing)
        self.start()

        # register with the queue

    # get blockchain from neighbors when starting up
    def get_blockchain(self) -> Optional[Blockchain]:
        if not self.testing:
            n: int = random.choice(self.neighbors)
            r = requests.get(HOST + ":" + str(PORT + n) + "/get_blockchain")
            logging.debug("Got raw blockchain from neighbors " + str(r.content))
            return Blockchain.deserialize(r.content)

    # main loop that runs the verifier
    def run(self) -> None:
        i = 0
        while True:
            i += 1
            
            # found a completed block
            if (self.new_block > 0):
                logging.debug("Found block {i}")
                potential_block = self.blocks_to_verify[-1]

                # validate the transactions in the block
                valid = potential_block.transactions[0].amount < REWARD
                l = self.blockchain.get_len()
                for i in range(1, len(potential_block.transactions)):
                    t = potential_block.transactions[i]
                    valid &= self.blockchain.verify_transaction(t, l, i)
                if not valid:
                    logging.debug("Invalid transaction found.")

                # validate proof of work
                valid &= potential_block.validate_POW(self.blockchain.get_top())

                if valid:
                    self.blockchain.add_block(potential_block)
                    self.blocks_to_verify.remove(potential_block)
                    logging.debug("Added block " + potential_block.serialize())
                else:
                    logging.debug("Rejected block " + potential_block.serialize())
                self.new_block -= 1

            sleep(0.01)


# TODO
# test with fake blocks for verifier
# test verifier communication
