import argparse
from ilpcoin.ilp_queue.ilp_queue import *

def main():
    print("Starting ilpqueue")
    parser = argparse.ArgumentParser()
    parser.add_argument("-host", help="Server hostname", type=str, default='localhost')
    parser.add_argument("-port", help="Server port number", type=int, default='7000')
    args = parser.parse_args()

    HOST = args.host
    PORT = int(args.port)

    app.run(host=HOST, port=PORT)

if __name__ == '__main__':
    main()
