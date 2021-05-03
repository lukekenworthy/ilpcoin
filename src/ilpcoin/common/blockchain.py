#!usr/bin/env python3

import hashlib
from typing import List, Optional
from ilpcoin.common.ilp import *
from ilpcoin.common.constants import *
import requests
import logging

class BadTransactionError(Exception):
    pass

class BadBlockError(Exception):
    pass

class Transaction:

    '''Represents a transaction, a group of which comprise a block. 

    Attributes
    ----------
    sender : string
        The user who sends this transaction.
    receiver : string
        The receiver of the transaction. 
    amount : int
        The amount of ilpcoin transferred. 
    '''

    def __init__(self, sender:str='', receiver: str='', amount: int=0):
        '''Initializes a transaction.'''
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def __eq__(self, other:'Transaction'):
        check = self.sender == other.sender
        check &= self.receiver == other.receiver
        check &= self.amount == other.amount
        return check
        
    def hash(self) -> str:
        '''Generate the sha256 hash of this transaction.'''
        to_hash = bytes(self.sender+self.receiver+str(self.amount), 'utf-8')
        return hashlib.sha256(to_hash).hexdigest()
    
    def serialize(self) -> bytes:
        '''Serialize this transaction to bytes, using pickle.'''
        return pickle.dumps(self)
    
    @classmethod
    def deserialize(cls, data: bytes):
        '''Inverse of serialize. Returns a Transaction.'''
        return pickle.loads(data)

class Block:

    '''Encapsulates all information about a block in the chain

    Attributes
    ----------
    transactions : List[Transaction]
        The transactions in the block.
    prev_hash : str
        The sha256 hash of the previous block in the chain. 
    ILP : int 
        The global uid of the Ilp associated with this block. 
    ILP_solution : Optional[IlpSolution]
        The solution to the ILP. Note that, unlike the ILP, the entire solution object is stored on the blockchain. 
    nonce : int 
        The nonce discovered to solve this block.
    testing : bool 
        Set to false, except when running the test suite. 
    '''
    
    def __init__(self, transactions: List[Transaction]=[], prev_hash: str='', nonce:int = 0, 
    ILP: int=0, ILP_solution: Optional[IlpSolution]=None, testing=False):
        '''Initialize a new block.'''
        self.transactions: List[Transaction] = transactions
        self.prev_hash: str = prev_hash
        self.ILP: int = ILP
        self.ILP_solution: Optional[IlpSolution] = ILP_solution
        self.nonce: int = nonce
        self.testing = testing
    
        prev_hash, nonce, ILP, ILP_solution

    def __eq__(self, other: 'Block'):
        '''For testing, it is necessary to be able to compare blocks.'''
        check: bool = True
        for (t1, t2) in zip(self.transactions, other.transactions):
            check &= t1 == t2
        check &= self.prev_hash == other.prev_hash
        check &= self.ILP == other.ILP
        check &= self.ILP_solution.variable_results == other.ILP_solution.variable_results
        check &= self.nonce == other.nonce
        return check

    def serialize(self) -> bytes:
        '''Serialize this block to bytes, using pickle.'''
        return pickle.dumps(self)

    @classmethod
    def deserialize(cls, data: bytes) -> 'Block':
        '''Inverse of serialize. Returns a Block.'''
        return pickle.loads(data)
    
    def hash(self) -> str:
        '''Generate the sha256 hash of this block.'''
        to_hash = self.ILP_solution.serialize() + bytes(str(self.nonce) + self.prev_hash, 'utf-8')
        for t in self.transactions:
            to_hash += t.serialize()
        return hashlib.sha256(to_hash).hexdigest()
    
    def validate_top_of_queue(self):
        '''Inform the queue that the Ilp ahs been solved, and return true if the queue accepts the solution. 

        The queue will reject the solution if the Ilp is stale, and the chain has moved on to solving subsequent Ilps.'''
        r = requests.get(QUEUE_HOST + ":" + str(QUEUE_PORT) + "/get_top_ilp")
        top_ILP = Ilp.deserialize(r.content)
        return self.ILP == top_ILP.get_id()

    def validate_block(self, previous: Optional['Block'], hardness: int) -> bool:
        '''The primary verification routine. Uses the previous block to check that the hashes are valid, 
        the transactions are valid, and the solution solves the Ilp.

        This is used by both miners and verifiers to validate blocks.
        '''
        check: bool = self.validate_nonce(hardness)

        # check that the previous_hash is correct
        if previous:
            check &= previous.hash() == self.prev_hash 
            logging.debug(f"Previous hash was correct? {check}")
        
        if not self.testing:
            r = requests.get("http://" + QUEUE_HOST + ":" + str(QUEUE_PORT) + "/" + 'get_ilp_by_id/' + str(self.ILP))
            if r.text == ILP_NOT_FOUND:
                logging.debug(f"ILP_NOT_FOUND id {self.ILP}")
                return False 
            else:
                full_ILP = Ilp.deserialize_s(r.text)
                if self.ILP_solution:
                    check &= full_ILP.check(self.ILP_solution)
        if self.transactions != []:
            check &= self.transactions[0].sender == self.transactions[0].receiver
            check &= self.transactions[0].amount == REWARD 
        
        logging.debug(f"Block successfully validated? {check}")
        return check
    
    def validate_nonce(self, hardness: int) -> bool:
        '''Ensure that the nonce solves the hash puzzle for this block. Both miners and verifiers should use this method to validate a nonce.'''
        try:
            return int(self.hash()[len(self.hash()) - hardness:]) == 0
        except:
            logging.debug("Found a bad nonce")
            return False
    
    def set_nonce(self, nonce:int) -> None:
        '''Used by miners to set the nonce for this block. '''
        self.nonce = nonce


class Blockchain:
    def __init__(self, blocks: List[Block]=[]):
        self.blockchain: List[Block] = blocks
    
    def __eq__(self, other: 'Blockchain'):
        check: bool = True
        for (b1, b2) in zip(self.blockchain, other.blockchain):
            check &= b1 == b2
        return check
    
    def serialize(self) -> bytes:
        return pickle.dumps(self)
    
    @classmethod
    def deserialize(cls, data:bytes) -> None:
        return pickle.loads(data)
    
    def get_top(self) -> Optional[Block]:
        if self.blockchain == []:
            return None
        else:
            return self.blockchain[len(self.blockchain) - 1]
    
    def add_block(self, block: Block):
        self.blockchain.append(block)
    
    # returns the amount of money that user has in the blockchain
    def get_value_by_user(self, user: str, block_index: int, trans_index: int) -> int:
        amount = 0

        # pool up all the money owned by this sender
        for block in self.blockchain[:block_index]:

            # handle transaction fee
            if user == block.transactions[0].sender:
                amount += block.transactions[0].amount

            for t in block.transactions[1:trans_index]:
                if t.sender == user:
                    amount -= t.amount
                if t.receiver == user:
                    amount += t.amount
        return amount
    
    # everyone should use this method to verify that a transaction does not double spnd
    def verify_transaction(self, transaction: Transaction, block_index: int, trans_index: int) -> bool:
        amount = self.get_value_by_user(transaction.sender, block_index, trans_index)
        return not (amount < transaction.amount)
    
    def get_len(self) -> int:
        return len(self.blockchain)
    
    # get an ILP solution by id -> used by the queue to service clients 
    def get_solution_by_id(self, id:int) ->  Optional[IlpSolution]:
        for b in self.blockchain:
            if int(b.ILP) == int(id):
                return b.ILP_solution
        return None
    
    # verify the entire blockchain for consistency and valid POWs
    def verify_blockchain(self) -> bool:
        previous = None
        for i in range(len(self.blockchain)):
            if not self.blockchain[i].validate_block(previous, HARDNESS):
                return False 
            previous = self.blockchain[i]
            
            # skip genesis transaction - that's a blockwide property
            for t in range(1, len(self.blockchain[i].transactions[1:])):
                if not self.verify_transaction(self.blockchain[i].transactions[t], i, t):
                    return False 
        return True 

    