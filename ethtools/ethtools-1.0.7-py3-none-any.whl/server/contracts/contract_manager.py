import json

from ethtools.server.web_server import WebServer

class Contract():
    def __init__(self):
        self.name = ""
        self.scope = 0
        self.abi = ""
        self.address = ""

    def to_json(self):
        return {"name": self.name, "address": self.address, "abi": self.abi}


class ContractStorage():
    def __init__(self):
        self.storage = []

    def add(self, contract):
        new_contract = self.get_by_name(contract.name, contract.scope)
        if new_contract is None:
            self.storage.append(contract)
            return True
        else:
            new_contract.abi = contract.abi
            new_contract.address = contract.address
            return False
                   
    def get_by_name(self, name, scope):
        for contract in self.storage:
            if contract.name == name and contract.scope == scope:
                return contract
        return None


class ContractManager():
    def __init__(self):
        self.contract_storage = ContractStorage()

    def create_contract(self, scope, name, sender, abi, bytecode, args):
        contract = Contract()

        contract.scope = scope
        contract.name = name
        contract.abi = abi

        w3_contract = WebServer().w3.eth.contract(abi=abi, bytecode=bytecode)
        tx_hash = w3_contract.deploy(transaction={'from': sender}, args=args)
        tx_receipt = None  

        while(tx_receipt is None):
            tx_receipt = WebServer().w3.eth.getTransactionReceipt(tx_hash)

        contract.address = tx_receipt['contractAddress']
        self.contract_storage.add(contract)

        return contract.to_json()

    def get_contract(self, scope, name):
        contract = self.contract_storage.get_by_name(name, scope)

        if contract == None:
            return {}
        else:
            return contract.to_json()

    