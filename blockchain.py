#!usr/bin/env python3

class BadTransactionError(Exception):
    pass

class Block:
    
    def __init__(self, transactions):
        self.transactions = transactions

class Transaction:

    def __init__(self, transaction: dict): 
        self.transaction = transaction
        self.validate()

    def validate(self) -> None: 
        if ("sender" not in self.transaction or "reciever" not in self.transaction 
        or "amount" not in self.transaction):
            raise BadTransactionError

    


    