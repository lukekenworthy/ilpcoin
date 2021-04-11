# example inspired by https://docs.python-mip.com/en/latest/examples.html


from mip import Model, xsum, maximize, BINARY, minimize
from ilpcoin.common.ilp import Ilp

p = [10, 13, 18, 31, 7, 15]
w = [11, 15, 20, 35, 10, 33]
c, I = 47, range(len(w))

m = Model("knapsack")

x = [m.add_var(var_type=BINARY) for i in I]

m.objective = minimize(-1*xsum(p[i] * x[i] for i in I))

m += xsum(w[i] * x[i] for i in I) <= c

def knapsack():
    return Ilp(m, -.999)