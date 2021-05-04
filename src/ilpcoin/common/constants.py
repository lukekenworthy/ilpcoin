# Config
BLOCKSIZE = 5                   # transactions per block
HOST = 'localhost'              # verifier host
PORT = 8000                     # verifier port
REWARD = 5                      # block reward
QUEUE_HOST = 'localhost'        # queue host
QUEUE_PORT = 9000               # queue port
VERIFIERS_NEEDED = 3            # verifiers required per ILP

# Error codes for the verifier
ILP_NOT_FOUND = 'ERR_2'   
SUCCESS = 'SUCCESS'
INVALID_TRANSACTION = 'ERR_3'
HARDNESS = 2
INVALID_NONCE_OR_POW = 'ERR_4'
EMPTY_CHAIN = 'ERR_5'

# Error codes for the queue
FAILURE = 'FAILURE'
NOT_TOP_ILP = 'NOT_TOP_ILP'
TIMEOUT = 'TIMEOUT'
NO_VERIFIERS = 'NO_VERIFIERS'

# ILP hardness
ILP_HARDNESS = 6