from typing import Optional
import unittest
import random
import pytest
from ilpcoin.common.blockchain import Transaction, Block, Blockchain
from ilpcoin.common.ilp import *
from ilpcoin.common.sample_ilps.knapsack import *

ILP: Optional[Ilp] = knapsack()
ILP_solution: Optional[IlpSolution] = None

class SerializationTests(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        global ILP_solution
        ILP_solution = ILP.solve()

    def test_transaction_deserialize(self):
        # setup
        t = Transaction(sender='lavanya', receiver='jordan', amount=5)

        self.assertTrue(t == Transaction.deserialize(t.serialize()))

    def test_block_serialize(self):

        # setup
        t = Transaction(sender='lavanya', receiver='jordan', amount=5)

        b1 = Block(transactions=[t], prev_hash = '', nonce=0, ILP=0, ILP_solution=ILP_solution)
        b2 = Block.deserialize(b1.serialize())

        self.assertEqual(b1, b2)

    def test_blockchain_serialize(self):

        # setup
        t = Transaction(sender='lavanya', receiver='jordan', amount=5)
        block = Block(transactions=[t], prev_hash = '', nonce=0, ILP=0, ILP_solution=ILP_solution)

        chain1 = Blockchain([block])
        chain2 = Blockchain.deserialize(chain1.serialize())
        self.assertEqual(chain1, chain2)

class BlockchainTests(unittest.TestCase):

    def setup(self):
        self.previous = Block(transactions=[], prev_hash='', nonce=0, ILP=0, ILP_solution=ILP_solution)
        self.hardness = 1

        self.b = Block(transactions=[], prev_hash = self.previous.hash(), nonce=41, ILP=0, ILP_solution=ILP_solution)

        # find a good nonce
        while not self.b.validate_nonce(self.hardness):
            self.b.nonce = random.randint(1, 1000)
        print(self.b.nonce)

    def test_validate_nonce(self):
        self.setup()
        self.assertTrue(self.b.validate_nonce(self.hardness))

    def test_falsify_nonce(self):
        self.setup()
        self.b.nonce = 0
        self.assertFalse(self.b.validate_nonce(self.hardness))

    def test_validate_POW(self):
        self.setup()
        self.assertTrue(self.b.validate_block(self.previous, self.hardness))

    def test_falsify_POW(self):
        self.setup()
        self.b.prev_hash = ''
        self.assertFalse(self.b.validate_block(self.previous, self.hardness))

    def test_verify_transaction(self):

        # lav mined this block
        t0 = Transaction(sender="lav", receiver="lav", amount=5)

        # some transactions
        t1 = Transaction(sender="lav", receiver="luke", amount=3)
        t2 = Transaction(sender="luke", receiver="lav", amount=1)
        t3 = Transaction(sender="lav", receiver="luke", amount=1)
        t4 = Transaction(sender="lav", receiver="luke", amount=10)

        b = Blockchain(blocks=[Block(transactions=[t0, t1, t2, t3, t4], ILP=0, ILP_solution=ILP_solution)])

        # ignoring t4
        self.assertTrue(b.verify_transaction(t3, 2, 3))

        # including t4
        self.assertFalse(b.verify_transaction(t3, 2, 5))


