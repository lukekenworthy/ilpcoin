# example inspired by https://docs.python-mip.com/en/latest/examples.html
from mip import Model, xsum, maximize, BINARY, minimize
from ilpcoin.common.ilp import Ilp
import random

def random_knapsack(): 
    """Return a knapsack Ilp with random weights and values.
    
    Return an instance of our custom ILP class representing 
    the decision version of a random knpasack problem with 
    a value of k = 40.
    """
    # constants 
    p = [random.randint(0,35) for x in range(6)]
    w = [random.randint(0,35) for x in range(6)]
    c, I = 47, range(len(w))

    m = Model("knapsack")

    # add variables
    x = [m.add_var(var_type=BINARY) for i in I]

    # set objective function
    m.objective = maximize(xsum(p[i] * x[i] for i in I))

    # add constraints
    m += xsum(w[i] * x[i] for i in I) <= c


    return Ilp(m, 40, -1, True)
