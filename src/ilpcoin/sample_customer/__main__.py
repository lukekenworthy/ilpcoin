import argparse
import requests
import time
from ilpcoin.common.sample_ilps.traveling_salesman import traveling_salesman
from ilpcoin.common.sample_ilps.knapsack import knapsack
from ilpcoin.common.constants import *
from ilpcoin.common.ilp import *

def main():
    print("Sending TSM")
    demo_ilp = traveling_salesman()
    r = requests.post(QUEUE_HOST + ":" + str(QUEUE_PORT) + "/add_ilp",  data = {'ilp': demo_ilp.serialize()})
    tsm_id = r.content
    print("Received id of: " + str(tsm_id))

    print("Sending Knapsack")
    demo_ilp = knapsack()
    r = requests.post(QUEUE_HOST + ":" + str(QUEUE_PORT) + "/add_ilp",  data = {'ilp': demo_ilp.serialize()})
    knapsack_id = r.content
    print("Received id of: " + str(knapsack_id))

    print("Looking up ilps: ")
    tsm_raw = requests.get(QUEUE_HOST + ":" + str(QUEUE_PORT) + "/get_ilp_by_id/" + str(tsm_id)).content
    tsm_back = Ilp.deserialize(tsm_raw)
    knapsack_raw = requests.get(QUEUE_HOST + ":" + str(QUEUE_PORT) + "/get_ilp_by_id/" + str(knapsack_id)).content
    knapsack_back = Ilp.deserialize(knapsack_raw)

    print("Sleeping for 30 seconds to allow chain to do its thing.")
    time.sleep(30)

    print("Looking up solutions: ")
    r = requests.get(QUEUE_HOST + ":" + str(QUEUE_PORT) + "/get_solution_by_id/" + str(tsm_id))
    tsm_soln = IlpSolution.deserialize(r.content)
    r = requests.get(QUEUE_HOST + ":" + str(QUEUE_PORT) + "/get_solution_by_id/" + str(knapsack_id))
    knapsack_soln = IlpSolution.deserialize(r.content)

    print("Got solutions")
    print("Tsm correct?: " + str(tsm_back.check(tsm_soln)))
    print("Knapsack correct?: " + str(knapsack_back.check(knapsack_soln)))

if __name__ == '__main__':
    main()
 