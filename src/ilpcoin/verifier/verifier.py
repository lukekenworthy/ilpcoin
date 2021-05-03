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

    '''
    The verifier class represents a verifier. 

    Attributes
    ----------
    Inherits id, host, port, testing, blockchain, blocks_to_verify from Server superclass. 
    
    testing : bool 
        Testing mode enabled? Set to false unless working with the unit testing suite. 
    neighbors : List[str]
        A list of other verifiers with whom this verifier should publish blocks. 
    '''

    def __init__(self, id:int, host: str=HOST, port: int=PORT, testing=False):
        '''Initialize a verifier and a server. '''
        self.testing: bool = testing

        self.get_neighbors(id)

        b = self.get_blockchain()
        # verifiers after the first should not have empty chains
        while id != 1 and b.get_len() == 0:
            sleep(1)
            b = self.get_blockchain()
            logging.debug("Initialized to empty chain, sleeping for 1 second")

        super().__init__(id, b, host, port, testing)
        self.start()

        r = requests.get("http://" + QUEUE_HOST + ":" + str(QUEUE_PORT) + "/register_verifier/" + str(self.id))
        logging.debug("Registered with queue")
        self.block_queue: List[Dict] = []

        # genesis block -> only the first verifier should make this
        if self.id == 1:
            ilp = knapsack()
            ilp.set_id(0)
            b = Block([], '', 0, ilp.get_id(), ilp.solve())
            while not b.validate_nonce(HARDNESS):
                b.nonce = random.randrange(0, 1000000)
            self.blockchain.add_block(b)
            logging.debug("Made genesis block")

    
        def get_neighbors(self, id) -> None:
        '''Query the Ilp queue for a set of 5 neighbors that can be used to gossip new blocks. 
        
        Called on initialization. 
        '''
        if not self.testing:
            r = requests.get("http://" + QUEUE_HOST + ":" + str(QUEUE_PORT) + "/get_neighbors/5")
            self.neighbors = pickle.loads(r.content)
            self.neighbors = [int(el) for el in self.neighbors]
            if id in self.neighbors:
                self.neighbors.remove(id)
            logging.debug(f"Recieved {len(self.neighbors)} neighbors from queue")
        else:
            self.neighbors: List[int] = [1, 2]

    def get_blockchain(self) -> Optional[Blockchain]:
        '''Query neighbors to find the most up-to-date blockchain.'''
        if not self.testing:
            longest_chain = -1
            longest_neighbor = 0

            # figure out who has the longest fork
            for i in self.neighbors:
                r = requests.get("http://" + HOST + ":" + str(PORT + int(i)) + "/get_length")
                if int(r.content) > longest_chain:
                    longest_chain = int(r.content)
                    longest_neighbor = i
            
            logging.debug(f"Grabbing blockchain from neighbor id {longest_neighbor}")
            # grab their chain
            if longest_neighbor == 0:
                return Blockchain([])
            else:
                r = requests.get("http://" + HOST + ":" + str(PORT + longest_neighbor) + "/get_blockchain")
                return Blockchain.deserialize(r.content)
        else:
            return Blockchain(blocks=[])
    
    def advertise_block(self, b: Block, sender:int):
        '''Avertise block b to every known neighbor.'''
        headers = {"Content-Type":"application/binary",}
        if self.testing:
            return 
        for i in self.neighbors:
            if i != sender:
                url = f"http://{HOST}:{PORT + int(i)}/send_block/{self.id}" 
                r = requests.put(url, data=b.serialize(),headers=headers)
                logging.debug(f"Advertised block to neighbor {i}")

    def process_new_block(self, b: Block, sender:int) -> str:
        '''Verify that a new latest block, b, is valid, and add it to the blockchain on success.
        
        Also informs the queue of the newly verified block, so that the queue can progress to the next Ilp once enough
        verifiers have solved it.'''
        response = SUCCESS

        # validate the transactions in the block
        valid = b.transactions[0].amount < REWARD
        l = self.blockchain.get_len()

        # start from index 1 to skip the mining reward
        # may eventually want to optimize this 
        for i in range(1, len(b.transactions)):
            t = b.transactions[i]
            if not self.blockchain.verify_transaction(t, l, i):
                logging.debug(f"Found an invalid transaction at index {i}")
                response = INVALID_TRANSACTION
                break
        
        # validate static components - nonce, previous_hash, proof of work
        if not self.blockchain.get_top():
            logging.debug("top of the chain is None")
        if not b.validate_block(self.blockchain.get_top(), HARDNESS):
            response = INVALID_NONCE_OR_POW
            logging.debug(f"Found invalid nonce or proof of work")
        
        # add this block on the queue of stuff to be advertised
        if response == SUCCESS:
            logging.debug("Block has been verified successfully")
            self.blockchain.add_block(b)
            self.block_queue.append({"block":b, "sender":sender})
            # tell the queue that we verified a solution
            r = requests.get("http://" + QUEUE_HOST + ":" + str(QUEUE_PORT) + "/" + 'verify_ilp/' + str(b.ILP))
        return response
    

    def run(self):
        '''Run the block advertising routine indefinitely. 
        
        We want advertising to be concurrent to request processing else we risk system wide deadlock
        '''

        counter = 0

        while True:
            if self.block_queue != []:
                logging.debug(f"About to advertise my {counter}th block")
                self.advertise_block(self.block_queue[0]['block'], self.block_queue[0]['sender'])
                self.block_queue.pop(0)
                counter += 1
            else:
                sleep(0.1)


