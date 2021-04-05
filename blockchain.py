#!usr/bin/env python3

import json

class BadTransactionError(Exception):
    pass

class BadBlockError(Exception):
    pass

class Block:
    
    def __init__(self, transactions: list=[], hash: int=None):
        self.transactions: list = transactions
        self.hash: int = hash
        # waiting on jordan for exact rep, just leaving these guys as strings for now
        self.ILP: str = None
        self.ILP_solution: str = None

    def serialize(self) -> str:
        serialized_transactions = [el.serialize() for el in self.transactions]
        return json.dumps({"hash": self.hash, "ILP": self.ILP, "ILP_solution": self.ILP_solution,
        "transactions":serialized_transactions})

    def deserialize(self, data: str) -> None:
        raw_block: str = json.loads(data)
        try:
            self.hash: int = raw_block['hash']
            self.ILP: str = raw_block['ILP']
            self.ILP_solution:str = raw_block['ILP_solution']

            raw_transactions: str = raw_block["transactions"]
            self.transactions = [el.deserialize for el in raw_transactions]
        except:
            raise BadBlockError

    # leaving this to you luke, i guess this involves some hashing magic
    def validate_block(self):
        pass


class Transaction:

    def __init__(self, transaction: dict): 
        self.transaction = transaction
        self.validate()

    def validate(self) -> None: 
        if ("sender" not in self.transaction or "reciever" not in self.transaction 
        or "amount" not in self.transaction):
            raise BadTransactionError
    
    def serialize(self) -> str:
        return json.dumps(self.transaction)

    


    