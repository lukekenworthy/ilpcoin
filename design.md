# Design/Interfaces

## Client

* Each client needs a unique global ID
    * This can be done at deploy time (?)
    * Or the queue can manage UID's

Clients have three primary roles:

1. Miners
    * get_ILP(ID) int ID -> matrix ILP
        * asks for the ID'th ILP on the queue
    * solve_ILP(ILP) matrix ILP -> matrix solution
    * hash_solution(ILP, block) matrix ILP, list block -> int hash
        * blocks can be represented as a list of transaction
        * each transaction is a dictionary containing spender, reciever, and amount
2. Peers in a Peer to Peer Network
    * broadcast_solution(hash, ILP, solution, ID) int hash, matrix ILP, matrix solution, int ID -> None
        * inform queue and all peers that you've mined a block
    * recieve_broadcast() None ->  int hash, matrix ILP, matrix solution, int ID
        * nodes also act as servers in the P2P network validating other transactions
3. Nodes
    * verify_ILP_solution(hash, ILP, solution) int hash, matrix ILP, matrix solution -> bool
        * true if the solution is correct and the hash has the appropriate # of zeroes
    * verify_ILP(ILP, ID) matrix ILP, int ID -> bool
        * verify that this is indeed the correct ILP for this node
        * this means that the queue can't immediately pop the ILP off - it needs to give everyone some time to verify that it's correct 
        * mark it as stale maybe?

## Queue


