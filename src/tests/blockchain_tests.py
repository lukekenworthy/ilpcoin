import unittest
from ilpcoin.common.blockchain import Transaction, Block, Blockchain

class SerializationTests(unittest.TestCase):

    def test_transaction_equals(self):
        # setup
        t = Transaction()
        t.initialize(sender='lavanya', receiver='jordan', amount=5)

        self.assertTrue(t == Transaction().deserialize(t.serialize()))

    def test_transaction_serialize(self):
        # setup
        t = Transaction()
        t.initialize(sender='lavanya', receiver='jordan', amount=5)

        self.assertEqual(t.serialize(), '{"sender": "lavanya", "receiver": "jordan", "amount": 5}')

    def test_transaction_deserialize(self):
        t = Transaction()
        t.deserialize('{"sender": "lavanya", "receiver": "jordan", "amount": 5}')
        self.assertEqual(t.sender, 'lavanya')
        self.assertEqual(t.receiver, 'jordan')
        self.assertEqual(t.amount, 5)

    def test_block_serialize(self):

        # setup
        t = Transaction()
        t.initialize(sender='lavanya', receiver='jordan', amount=5)

        b1 = Block(transactions=[t], prev_hash = 0, nonce=0)
        b2 = Block()
        b2.deserialize(b1.serialize())

        self.assertEqual(b1, b2)

    def test_blockchain_serialize(self):

        # setup
        t = Transaction()
        t.initialize(sender='lavanya', receiver='jordan', amount=5)
        block = Block(transactions=[t], prev_hash = 0, nonce=0)

        chain1 = Blockchain([block], 5)
        chain2 = Blockchain().deserialize(chain1.serialize())
        self.assertEqual(chain1, chain2)


if __name__ == '__main__':
    unittest.main()
