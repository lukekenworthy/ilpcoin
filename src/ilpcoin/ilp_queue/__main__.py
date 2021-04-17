import argparse
from ilpcoin.ilp_queue.ilp_queue import *
from ilpcoin.common.constants import *

def main():
    print("Starting ilpqueue")
    parser = argparse.ArgumentParser()
    parser.add_argument("-host", help="Server hostname", type=str, default=QUEUE_HOST)
    parser.add_argument("-port", help="Server port number", type=int, default=QUEUE_PORT)
    args = parser.parse_args()

    HOST = args.host
    PORT = int(args.port)

    app.run(host=HOST, port=PORT)

if __name__ == '__main__':
    main()
