import argparse
from ilpcoin.ilp_queue.ilp_queue import *
from ilpcoin.common.constants import QUEUE_HOST, QUEUE_PORT
import ilpcoin.common.constants

def main():
    print("Starting ilpqueue")
    parser = argparse.ArgumentParser()
    parser.add_argument("-host", help="Server hostname", type=str, default=QUEUE_HOST)
    parser.add_argument("-port", help="Server port number", type=int, default=QUEUE_PORT)
    parser.add_argument("-verifiers", help="Number of verifiers needed to pop an ILP off the queue", type=int, default=VERIFIERS_NEEDED)
    args = parser.parse_args()

    HOST = args.host
    PORT = int(args.port)

    logging.basicConfig(filename='logs/queue.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)

    ilpcoin.common.constants.VERIFIERS_NEEDED=args.verifiers

    app.run(host=HOST, port=PORT)

if __name__ == '__main__':
    main()
