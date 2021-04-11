import unittest
import random
import pytest
from ilpcoin.common.blockchain import Transaction, Block, Blockchain
from ilpcoin.verifier.verifier import Verifier
import multiprocessing


class VerifierTests(unittest.TestCase):
    
    hardness = 0

    def setup(self):

        t0 = Transaction().initialize(sender="lav", receiver="lav", amount=5)

        # some transactions
        t1 = Transaction().initialize(sender="lav", receiver="luke", amount=3)
        t2 = Transaction().initialize(sender="luke", receiver="lav", amount=1)
        t3 = Transaction().initialize(sender="lav", receiver="luke", amount=1)
        t4 = Transaction().initialize(sender="lav", receiver="luke", amount=1)

        # this is the genesis block
        self.b0 = Block(transactions=[t0, t1 ], prev_hash='', nonce=0)
        while not self.b0.validate_nonce(0):
            self.b0.nonce = random.randint(1, 10000)
        
        self.verifier = Verifier(1, testing=True)

        self.verifier.blockchain = Blockchain([self.b0], blocksize=5)
    
    def test_valid_chain(self):

        self.setup()

        t0 = Transaction().initialize("luke", "lav", 1)
        b1 = Block(transactions=[t0], prev_hash = self.b0.hash(), nonce=0)
        while not b1.validate_nonce(self.hardness):
            b1.nonce = random.randint(1, 10000000000)

        # add the new block to the queue
        self.verifier.new_block = 1
        self.verifier.blocks_to_verify = [b1]

        # run the main verifier thread for 1 second
        #p = multiprocessing.Process(target=self.verifier.run)










