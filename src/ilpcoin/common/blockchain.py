#!usr/bin/env python3

import json
import hashlib
from ilpcoin.common.ilp import *

class BadTransactionError(Exception):
    pass

class BadBlockError(Exception):
    pass

class Transaction:

    def __init__(self):
        pass

    def __eq__(self, other):
        check = self.sender == other.sender
        check &= self.receiver == other.receiver
        check &= self.amount == other.amount
        return check
    
    def hash(self) -> bytes:
        to_hash = bytes(self.sender+self.receiver+self.amount, 'utf-8')
        return hashlib.sha256(to_hash).hexdigest()
    
    def initialize(self, sender:str, receiver: str, amount: int):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        return self 
    
    def serialize(self) -> bytes:
        return pickle.dumps(self)
    
    @classmethod
    def deserialize(self, data: bytes):
        return pickle.loads(data)

class Block:

    '''
    Encapsulates all information about a block in the chain
    '''
    
    def __init__(self, transactions: list=[], prev_hash: str='', nonce:int = 0):
        self.transactions: list = transactions
        self.prev_hash: str = prev_hash

        # ilp id
        self.ILP: int = 0

        # ilp solution
        self.ILP_solution = ''

        self.nonce: int = nonce
    
    def __eq__(self, other):
        check = True
        for (t1, t2) in zip(self.transactions, other.transactions):
            check &= t1 == t2
        check &= self.prev_hash == other.prev_hash
        check &= self.ILP == other.ILP
        check &= self.ILP_solution== other.ILP_solution
        check &= self.nonce == other.nonce
        return check

    def serialize(self) -> bytes:
        #serialized_transactions = [el.serialize() for el in self.transactions]        
        return pickle.dumps(self)
        #return json.dumps({"prev_hash": self.prev_hash, "ILP": str(self.ILP), "ILP_solution": str(self.ILP_solution.serialize()),
        #"nonce": self.nonce, "transactions":serialized_transactions})

    @classmethod
    def deserialize(self, data: bytes) -> None:
        return pickle.loads(data)
        '''raw_block: str = json.loads(data)
        try:
            self.prev_hash: int = int(raw_block['prev_hash'])
            self.ILP: int = int(raw_block['ILP'])
            self.ILP_solution:IlpSolution = IlpSolution.deserialize(raw_block['ILP_solution'])
            self.nonce: int = int(raw_block['nonce'])

            raw_transactions: str = raw_block["transactions"]
            self.transactions = [Transaction().deserialize(el) for el in raw_transactions]
            return self
        except:
            raise BadBlockError'''
    
    def hash(self) -> bytes:
        to_hash = bytes(self.ILP_solution + str(self.ILP) + str(self.nonce) + self.prev_hash, 'utf-8')
        for t in self.transactions:
            to_hash += t.hash()
        return hashlib.sha256(to_hash).hexdigest()

    # both miners and verifiers should use this method to validate blocks
    def validate_POW(self, previous, hardness: int) -> bool:

        # check that the previous_hash is correct
        check = previous.hash() == self.prev_hash 

        # check the ILP solution
            # waiting on queue
        # grab ILP from queue
        # check that it's the right ILP
        # check solution correctness

        # check that the hash puzzle was solved
        check &= self.validate_nonce(hardness)

        return check
    
    # both miners and verifiers should use this method to validate a nonce
    def validate_nonce(self, hardness: int) -> bool:
        try:
            return int(self.hash()[len(self.hash()) - hardness:]) == 0
        except:
            return False

class Blockchain:

    def __init__(self, blocks: list=None, blocksize: int=5):
        self.blockchain = blocks
        self.blocksize = 5
    
    def __eq__(self, other):
        check = True
        for (b1, b2) in zip(self.blockchain, other.blockchain):
            check &= b1 == b2
        return check
    
    def serialize(self) -> bytes:
        return pickle.dumps(self)
        #return json.dumps([b.serialize() for b in self.blockchain])
    
    @classmethod
    def deserialize(self, data:str) -> None:
        return pickle.loads(data)
        '''raw_chain = json.loads(data)
        self.blockchain = [Block().deserialize(el) for el in raw_chain]
        return self'''
    
    def get_top(self) -> Block:
        return self.blockchain[-1]
    
    def add_block(self, block: Block):
        self.blockchain.append(block)
    
    # everyone should use this method to verify that a transaction does not double spnd
    def verify_transaction(self, transaction: Transaction, block_index: int, trans_index: int) -> bool:
        amount = 0

        # pool up all the money owned by this sender
        for block in self.blockchain[:block_index]:

            # handle transaction fee
            if transaction.sender == block.transactions[0].sender:
                amount += block.transactions[0].amount

            for t in block.transactions[1:trans_index]:
                if t.sender == transaction.sender:
                    amount -= t.amount
                if t.receiver == transaction.sender:
                    amount += t.amount

        return not (amount < transaction.amount)

    