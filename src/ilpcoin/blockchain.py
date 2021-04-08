#!usr/bin/env python3

import json

class BadTransactionError(Exception):
    pass

class BadBlockError(Exception):
    pass

class Block:

    '''
    Encapsulates all information about a block in the chain
    '''
    
    def __init__(self, transactions: list=[], prev_hash: int=None):
        self.transactions: list = transactions
        self.prev_hash: int = prev_hash

        # waiting on jordan for exact rep, just leaving these guys as strings for now
        self.ILP: str = None
        self.ILP_solution: str = None

        self.nonce: int = None

    def serialize(self) -> str:
        serialized_transactions = [el.serialize() for el in self.transactions]
        return json.dumps({"prev_hash": self.prev_hash, "ILP": self.ILP, "ILP_solution": self.ILP_solution,
        "nonce": self.nonce, "transactions":serialized_transactions})

    def deserialize(self, data: str) -> None:
        raw_block: str = json.loads(data)
        try:
            self.prev_hash: int = int(raw_block['prev_hash'])
            self.ILP: str = raw_block['ILP']
            self.ILP_solution:str = raw_block['ILP_solution']
            self.nonce: int = int(raw_block['nonce'])

            raw_transactions: str = raw_block["transactions"]
            self.transactions = [Transaction().deserialize(el) for el in raw_transactions]
        except:
            raise BadBlockError
    
    def __hash__(self):
        return hash((self.ILP_solution, self.nonce, [hash(t) for t in self.transactions], self.prev_hash))

    # both miners and verifiers should use this method to validate blocks
    def validate_POW(self, previous, hardness: int) -> bool:

        # check that the previous_hash is correct
        check = hash(previous) == self.prev_hash

        # check the ILP solution

        # check that this is the correct ILP off the queue

        # check that the hash puzzle was solved
        check &= self.validate_nonce(hardness)

        return True
    
    # both miners and verifiers should use this method to validate a nonce
    def validate_nonce(self, hardness: int) -> bool:
        return str(hash(self))[0:hardness] == ("").join(['0' for i in range(0, hardness)])

class Transaction:

    def __init__(self):
        pass
    
    def initialize(self, sender:str, receiver: str, amount: int):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
    
    def serialize(self) -> str:
        return json.dumps({'sender': self.sender, 'receiver': self.receiver, 'amount': self.amount})
    
    def deserialize(self, data: str):
        raw_data = json.loads(data)
        self.initialize(sender=raw_data['sender'], receiver=raw_data['receiver'], amount=raw_data['amount'])
    
class Blockchain:

    def __init__(self, blockchain: list=None, blocksize: int = 5):
        self.blockchain = blockchain
        self.transactions = None
        self.blocksize = blocksize
    
    def serialize(self) -> str:
        return json.dumps([b.serialize() for b in self.blockchain])
    
    def deserialize(self, data:str) -> None:
        raw_chain = json.loads(data)
        self.blockchain = [Block().deserialize(el) for el in raw_chain]
    
    def get_top(self) -> Block:
        return self.blockchain[-1]
    
    def add_block(self, block: Block):
        self.blockchain.append(block)
    
    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)
    
    # everyone should use this method to verify that a transaction does not double spnd
    def verify_transaction(self, transaction: Transaction) -> bool:
        amount = 0

        # pool up all the money owned by this sender
        for block in self.blockchain:
            for t in block.transactions:
                if (t.sender == transaction.sender):
                    amount -= t.amount
                if (t.receiver == transaction.sender):
                    amount += t.amount
        return not (amount < transaction.amount)
    
    def block_ready(self) -> bool:
        return len(self.transactions > self.blocksize)

    