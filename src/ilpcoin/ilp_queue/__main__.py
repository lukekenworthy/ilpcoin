import argparse
from ilpcoin.ilp_queue.ilp_queue import *
from ilpcoin.common.constants import QUEUE_HOST, QUEUE_PORT
import ilpcoin.common.constants
import os

def main():
    '''Launches the IlpQueue Flask app. Invoke with -h for more information on parameters'''

    print("Starting ilpqueue")
    parser = argparse.ArgumentParser()
    parser.add_argument("-host", help="Server hostname", type=str, default=QUEUE_HOST)
    parser.add_argument("-port", help="Server port number", type=int, default=QUEUE_PORT)
    parser.add_argument("-verifiers", help="Number of verifiers needed to pop an ILP off the queue", type=int, default=VERIFIERS_NEEDED)
    args = parser.parse_args()

    HOST = args.host
    PORT = int(args.port)

    # Configure logging
    try:
        os.mkdir("logs/")
    except FileExistsError:
       None

    # logging initialization
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    logging.basicConfig(filename='logs/queue.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)

    # Specify verifiers needed
    ilpcoin.common.constants.VERIFIERS_NEEDED=args.verifiers

    app.run(host=HOST, port=PORT)

if __name__ == '__main__':
    main()
