import argparse
import requests
from ilpcoin.common.sample_ilps.traveling_salesman import traveling_salesman
from ilpcoin.common.constants import *

def main():
    demo_ilp = traveling_salesman()
    r = requests.post(QUEUE_HOST + ":" + str(QUEUE_PORT) + "/add_ilp",  data = {'ilp': demo_ilp.serialize()})
    print("Received: " + str(r))

if __name__ == '__main__':
    main()
 