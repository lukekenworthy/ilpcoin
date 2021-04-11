import unittest
import random
import pytest
from ilpcoin.common.blockchain import Transaction, Block, Blockchain

class VerifierTests(unittest.TestCase):
    
    def setup(self):
        t0 = Transaction().initialize(sender="lav", receiver="lav", amount=5)

        # some transactions
        t1 = Transaction().initialize(sender="lav", receiver="luke", amount=3)
        t2 = Transaction().initialize(sender="luke", receiver="lav", amount=1)
        t3 = Transaction().initialize(sender="lav", receiver="luke", amount=1)
        t4 = Transaction().initialize(sender="lav", receiver="luke", amount=10)
