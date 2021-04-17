import argparse
from typing import Optional

from ilpcoin.miner.client import ClientPeer 
from ilpcoin.common.constants import *
import logging

miner: Optional[ClientPeer] = None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-id", help="Node Id", type=int, default=0)
    args = parser.parse_args()

    #logging.basicConfig(filename='logs/verifier' + str(args.id) + '.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    logging.basicConfig(level=logging.DEBUG)

    miner = ClientPeer(id=args.id)
    miner.start_mine()

if __name__ == '__main__':
    main()
 