#!usr/bin/env python3

from server import Server
from time import sleep
from ilpcoin.blockchain import *
import argparse
import random
import requests

HOST:str = 'localhost'
PORT:int = 8000

class Verifier(Server):

    def __init__(self, id:int, reward:int = 6, host: str=HOST, port: int=PORT, testing=False):

        # hardcoded for now - eventually we will ask the queue for these
        self.neighbors = [1, 2, 3].remove(id)

        super().__init__(id, self.get_blockchain(), host, port, testing)
        self.start()
        self.reward = reward

        # set of verified transactions waiting to be added to a block
        self.transactions = None

    # get blockchain from neighbors when starting up
    def get_blockchain(self) -> Blockchain:
        n: int = random.choice(self.neighbors)
        r = requests.get(HOST + ":" + str(PORT + n) + "/get_blockchain")
        return Blockchain().deserialize(r.content)
    
    # do we have enough transactions to make a new block
    def block_ready(self):
        return len(self.transactions > self.blocksize)
    
    # main loop that runs the verifier
    def run(self) -> None:
        while True:

            # found a completed block
            if (self.new_block > 0):
                blockchain = self.blockchain()

                potential_block = self.blocks_to_verify[-1]

                # validate the transactions in the block
                valid = potential_block.transactions[0].amount < self.reward
                for t in potential_block.transactions[1:]:
                    valid &= blockchain.verify_transaction(t)
                
                # validate proof of work
                valid &= potential_block.validate_POW(blockchain.get_top())

                if valid:
                    blockchain.add(potential_block)
                    self.blocks_to_verify.remove(potential_block)
                    print('ADDED BLOCK')
                else:
                    print('BAD BLOCK')
                self.new_block -= 1
            
            # found a new transaction
            if (self.new_transaction):
                pass
                '''
                potential_transaction = self.server.transactions_to_verify[-1]
                if self.server.blockchain.verify_transaction(potential_transaction):
                    self.server.blockchain.add_transaction(potential_transaction)
                    self.server.transactions_to_verify.remove(potential_transaction)
                self.server.new_transaction = False'''
            


            sleep(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-id", help="Node Id", type=int, default=0)
    parser.add_argument("-t", help=("Optional testing flag"), default=False)
    parser.add_argument("-host", help="Server hostname", type=str, default='localhost')
    parser.add_argument("-port", help="Server port number", type=int, default='8000')
    
    HOST = args.host
    PORT = int(args.port)

    args = parser.parse_args()
    verifier = Verifier(id)
    verifier.run()
    

# TODO
# test other random blockchain methods
# test with fake blocks for verifier
# test verifier communication
# test transaction, POW, blockchain validation
