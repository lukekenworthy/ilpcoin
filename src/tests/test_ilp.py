import unittest
import random
import pytest
from ilpcoin.common.sample_ilps.knapsack import knapsack
from ilpcoin.common.ilp import *

class IlpTests(unittest.TestCase):
    def test_ilp_serialize(self):
        knapsack_model = knapsack()
        print(knapsack_model)
        reconstructed = Ilp.deserialize(knapsack_model.serialize())
        print("Reconstructed:" + str(reconstructed.mip_ilp.objective))
        print("Orig:" + str(knapsack_model.mip_ilp.objective))

        print("Reconstructed:" + str(reconstructed.mip_ilp.vars[3]))
        print("Orig:" + str(knapsack_model.mip_ilp.vars[3]))

        self.assertTrue(knapsack_model == reconstructed)

    def test_ilp_solve(self): 
        knapsack_model = knapsack()
        soln = knapsack_model.solve()
        print("vars,", str(soln.variable_results))
        self.assertTrue(knapsack_model.check(soln))
    
    def test_ilp_solve_reconst(self): 
        knapsack_model = knapsack()
        print(knapsack_model)
        reconstructed = Ilp.deserialize(knapsack_model.serialize())
        soln = reconstructed.solve()
        print("vars,", str(soln.variable_results))
        self.assertTrue(reconstructed.check(soln))