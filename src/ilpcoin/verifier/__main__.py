import argparse
from typing import Optional
from ilpcoin.verifier.verifier import Verifier
import logging

verifier: Optional[Verifier] = None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-id", help="Node Id", type=int, default=0)
    parser.add_argument("-t", help=("Optional testing flag"), default=True)
    parser.add_argument("-host", help="Server hostname", type=str, default='localhost')
    parser.add_argument("-port", help="Server port number", type=int, default='8000')
    args = parser.parse_args()

    logging.basicConfig(filename='logs/verifier.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    logging.basicConfig(level=logging.DEBUG)

    global verifier
    verifier = Verifier(id=args.id, host=HOST, port=PORT, testing=args.t)
    verifier.run()

if __name__ == '__main__':
    main()
