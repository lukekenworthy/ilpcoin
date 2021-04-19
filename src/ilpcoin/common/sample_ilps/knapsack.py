# example inspired by https://docs.python-mip.com/en/latest/examples.html

from mip import Model, xsum, maximize, BINARY, minimize
from ilpcoin.common.ilp import Ilp

# constants 
p = [10, 13, 18, 31, 7, 15]
w = [11, 15, 20, 35, 10, 33]
c, I = 47, range(len(w))

m = Model("knapsack")

# add variables
x = [m.add_var(var_type=BINARY) for i in I]

# set objective function
m.objective = maximize(xsum(p[i] * x[i] for i in I))

# add constraints
m += xsum(w[i] * x[i] for i in I) <= c

# create a instance of our 
# custom ILP class representing the decision version of
# our problem, and a value of k = 40
def knapsack():
    return Ilp(m, 40)