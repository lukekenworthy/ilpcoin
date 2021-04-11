import unittest
import random
import pytest
from ilpcoin.common.blockchain import Transaction, Block, Blockchain
import mip
from ilpcoin.common.ilp import *

class SerializationTests(unittest.TestCase):

    def test_transaction_deserialize(self):
        # setup
        t = Transaction()
        t.initialize(sender='lavanya', receiver='jordan', amount=5)

        self.assertTrue(t == Transaction.deserialize(t.serialize()))

    def test_block_serialize(self):

        # setup
        t = Transaction()
        t.initialize(sender='lavanya', receiver='jordan', amount=5)

        b1 = Block(transactions=[t], prev_hash = 0, nonce=0)
        b2 = Block().deserialize(b1.serialize())

        self.assertEqual(b1, b2)

    def test_blockchain_serialize(self):

        # setup
        t = Transaction()
        t.initialize(sender='lavanya', receiver='jordan', amount=5)
        block = Block(transactions=[t], prev_hash = 0, nonce=0)

        chain1 = Blockchain([block], 5)
        chain2 = Blockchain.deserialize(chain1.serialize())
        self.assertEqual(chain1, chain2)

class BlockchainTests(unittest.TestCase):

    def setup(self):
        self.previous = Block(transactions=[], prev_hash='', nonce=0)
        self.hardness = 1

        self.b = Block(transactions=[], prev_hash = self.previous.hash(), nonce=41)

        # find a good nonce
        while not self.b.validate_nonce(self.hardness):
            self.b.nonce = random.randint(1, 1000)

    def test_validate_nonce(self):
        self.setup()
        self.assertTrue(self.b.validate_nonce(self.hardness))

    def test_falsify_nonce(self):
        self.setup()
        self.b.nonce = 0
        self.assertFalse(self.b.validate_nonce(self.hardness))

    def test_validate_POW(self):
        self.setup()
        self.assertTrue(self.b.validate_POW(self.previous, self.hardness))

    def test_falsify_POW(self):
        self.setup()
        self.b.prev_hash = ''
        self.assertFalse(self.b.validate_POW(self.previous, self.hardness))

    def test_verify_transaction(self):

        # lav mined this block
        t0 = Transaction().initialize(sender="lav", receiver="lav", amount=5)

        # some transactions
        t1 = Transaction().initialize(sender="lav", receiver="luke", amount=3)
        t2 = Transaction().initialize(sender="luke", receiver="lav", amount=1)
        t3 = Transaction().initialize(sender="lav", receiver="luke", amount=1)
        t4 = Transaction().initialize(sender="lav", receiver="luke", amount=10)

        b = Blockchain(blocks=[Block(transactions=[t0, t1, t2, t3, t4])])

        # ignoring t4
        self.assertTrue(b.verify_transaction(t3, 2, 3))

        # including t4
        self.assertFalse(b.verify_transaction(t3, 2, 5))


