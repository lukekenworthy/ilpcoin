from ilpcoin.ilp_queue.ilp_queue import IlpQueue
from ilpcoin.common.ilp import *
from ilpcoin.common.sample_ilps.knapsack import knapsack
from ilpcoin.common.sample_ilps.traveling_salesman import traveling_salesman
import unittest
import random
import pytest
demo_queue_object = IlpQueue

class IlpQueueTests(unittest.TestCase):
    def test_queue_add_inc_pop(self): 
        ilp_queue = IlpQueue()
        test_ilp_1 = knapsack()
        test_ilp_2 = traveling_salesman()

        # add first one and make sure it's top
        ilp_queue.add(test_ilp_1)
        self.assertTrue(ilp_queue.get_top().get_id() == 1)
        self.assertTrue(ilp_queue.get_top() == test_ilp_1)

        # add second; first one is still top
        ilp_queue.add(test_ilp_2)
        self.assertTrue(ilp_queue.get_top() == test_ilp_1)
        self.assertTrue(ilp_queue.get_top().get_id() == 1)

        # look them up
        self.assertTrue(ilp_queue.lookup_ilp(1) == test_ilp_1)
        self.assertTrue(ilp_queue.lookup_ilp(2) == test_ilp_2)
        
        # missing returns None
        self.assertTrue(ilp_queue.lookup_ilp(3) == None)

        # not the top; does nothing
        self.assertTrue(not ilp_queue.incr_count(2))

        #verify top 3 times; this should pop the top
        self.assertTrue(ilp_queue.incr_count(1))
        self.assertTrue(ilp_queue.count == 1)
        self.assertTrue(ilp_queue.incr_count(1))
        self.assertTrue(ilp_queue.count == 2)
        self.assertTrue(ilp_queue.incr_count(1))
        self.assertTrue(ilp_queue.count == 0)

        # after that happens, top should have id 2, so this does nothing
        print("Count " + str(ilp_queue.count))
        print("top " + str(ilp_queue.get_top().get_id()))

        self.assertTrue(not ilp_queue.incr_count(1))
        self.assertTrue(ilp_queue.count == 0)

        # now the top ilp is 2
        self.assertTrue(ilp_queue.get_top().get_id() == 2)
        
        # verify 3 times
        self.assertTrue(ilp_queue.incr_count(2))
        self.assertTrue(ilp_queue.incr_count(2))
        self.assertTrue(ilp_queue.incr_count(2))

        self.assertTrue(ilp_queue.get_top() == None)
