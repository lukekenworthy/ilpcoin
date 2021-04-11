import unittest
import random
import pytest
from ilpcoin.common.sample_ilps.knapsack import knapsack
from ilpcoin.common.ilp import *


def ilp_solve_and_check(input_ilp): 
    soln = input_ilp.solve()
    # print("vars,", str(soln.variable_results))
    return input_ilp.check(soln)

def ilp_solve_post_serialization(input_ilp): 
    reconstructed = Ilp.deserialize(input_ilp.serialize())
    return ilp_solve_and_check(reconstructed)

def ilp_serialization_basic_properties(input_ilp): 
    reconstructed = Ilp.deserialize(input_ilp.serialize())
    return reconstructed.k == input_ilp.k and reconstructed.uid == input_ilp.uid

class IlpTests(unittest.TestCase):

    def test_ilp_solve_and_check_knapsack(self): 
        self.assertTrue(ilp_solve_and_check(knapsack()))

    def test_ilp_solve_post_serialization_knapsack(self): 
        self.assertTrue(ilp_solve_post_serialization(knapsack()))

    def test_ilp_serialization_basic_properties_knapsack(self): 
        self.assertTrue(ilp_serialization_basic_properties(knapsack()))

    # def test_ilp_serialize(self):
    #     knapsack_model = knapsack()
    #     print(knapsack_model)
    #     reconstructed = Ilp.deserialize(knapsack_model.serialize())
    #     print("Reconstructed:" + str(reconstructed.mip_ilp.objective))
    #     print("Orig:" + str(knapsack_model.mip_ilp.objective))

    #     print("Reconstructed:" + str(reconstructed.mip_ilp.vars[3]))
    #     print("Orig:" + str(knapsack_model.mip_ilp.vars[3]))

    #     self.assertTrue(knapsack_model == reconstructed)


    
