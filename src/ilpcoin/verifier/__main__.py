import argparse
from ilpcoin.verifier.verifier import *
import logging

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-id", help="Node Id", type=int, default=0)
    parser.add_argument("-t", help=("Optional testing flag"), default=False)
    parser.add_argument("-host", help="Server hostname", type=str, default='localhost')
    parser.add_argument("-port", help="Server port number", type=int, default='8000')
    args = parser.parse_args()

    HOST = args.host
    PORT = int(args.port)

    logging.basicConfig(filename='verifier.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    logging.basicConfig(level=logging.DEBUG)

    verifier = Verifier(id, host=HOST, port=PORT, testing=args.t)
    verifier.run()

if __name__ == '__main__':
    main()
