import argparse
import requests
import time
from ilpcoin.common.sample_ilps.traveling_salesman import traveling_salesman
from ilpcoin.common.sample_ilps.knapsack import knapsack
from ilpcoin.common.constants import *
from ilpcoin.common.ilp import *

def main():
    queue_url = "http://" + QUEUE_HOST + ":" + str(QUEUE_PORT)
    print("Sending TSM")
    demo_ilp = traveling_salesman()
    r = requests.post(queue_url+ "/add_ilp",  data = {'ilp': demo_ilp.serialize_s()})
    tsm_id = int(r.content)
    print("Received id of: " + str((tsm_id)))

    print("Sending Knapsack")
    demo_ilp = knapsack()
    r = requests.post(queue_url+ "/add_ilp",  data = {'ilp': demo_ilp.serialize_s()})
    knapsack_id = int(r.content)
    print("Received id of: " + str(knapsack_id))

    print("Looking up ilps: ")
    tsm_raw = requests.get(queue_url+ "/get_ilp_by_id/" + str(tsm_id)).text
    tsm_back = Ilp.deserialize_s(tsm_raw)
    knapsack_raw = requests.get(queue_url+ "/get_ilp_by_id/" + str(knapsack_id)).text
    knapsack_back = Ilp.deserialize_s(knapsack_raw)

    print("Sleeping for 30 seconds to allow chain to do its thing.")
    time.sleep(30)

    print("Looking up solutions: ")
    r = requests.get(queue_url+ "/get_solution_by_id/" + str(tsm_id))
    print("sol1: " + str(r.text))
    tsm_soln = IlpSolution.deserialize_s(r.text)
    r = requests.get(queue_url+ "/get_solution_by_id/" + str(knapsack_id))
    knapsack_soln = IlpSolution.deserialize_s(r.text)

    print("Got solutions")
    print("Tsm correct?: " + str(tsm_back.check(tsm_soln)))
    print("Knapsack correct?: " + str(knapsack_back.check(knapsack_soln)))

if __name__ == '__main__':
    main()
 