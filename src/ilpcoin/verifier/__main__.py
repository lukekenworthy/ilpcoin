import argparse
from typing import Optional
from ilpcoin.verifier.verifier import Verifier
from ilpcoin.common.constants import *
import logging
import os

verifier: Optional[Verifier] = None

def main():
    '''Run the main verifier routine. Invoke the application with -h for information on CLI arguments.'''

    parser = argparse.ArgumentParser()
    parser.add_argument("-id", help="Node Id", type=int, default=0)
    parser.add_argument("-t", help=("Optional testing flag"), default=False)
    parser.add_argument("-host", help="Server hostname", type=str, default='localhost')
    parser.add_argument("-port", help="Server port number", type=int, default='8000')
    args = parser.parse_args()

    try:
        os.mkdir("logs/")
    except FileExistsError:
        pass

    # logging initialization
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(filename='logs/verifier' + str(args.id) + '.log', filemode='w', format='VERIFIER ID ' + str(args.id) + ' %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)

    global verifier
    verifier = Verifier(id=args.id, host=HOST, port=PORT, testing=args.t)
    verifier.run()

if __name__ == '__main__':
    main()
 