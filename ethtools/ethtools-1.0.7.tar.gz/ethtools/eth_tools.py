import requests
import json
import os
import re

from uuid import uuid4
from web3 import Web3, HTTPProvider
from web3.contract import ConciseContract

from .eth_types import Account, Contract
from .eth_properties import Filtered, Preloaded

w3 = Web3(HTTPProvider("http://localhost:8545/"))

class EthResolver:
    def __init__(self, eth_tools):
        self.eth = eth_tools

    def resolve_account_name(self, name):
        return self.eth.filter(role=name).accounts[0].address
    
    def resolve_accounts_name(self, name):
        data = []
        accounts = self.eth.filter(role=name).accounts
        for i in accounts:
            data.append(i.address)
        return data

    def resolve_contract_name(self, name):
        return self.eth.filter(name=name).contract.address

    def resolve_arg(self, arg):
        if type(arg) is list:
            return self.resolve_args(arg)
        if type(arg) is not str:
            return arg
        
        contract_patterns = re.findall('{{Contract:(\w+)}}', arg)
        if len(contract_patterns) > 0:
            return self.resolve_contract_name(contract_patterns[0])

        account_patterns = re.findall('{{Account:(\w+)}}', arg)
        if len(account_patterns) > 0:
            return self.resolve_account_name(account_patterns[0])

        accounts_patterns = re.findall('{{Accounts:(\w+)}}', arg)
        if len(accounts_patterns) > 0:
            return self.resolve_accounts_name(accounts_patterns[0])

        return arg

    def resolve_args(self, args):   
        resolved = []
        for arg in args:
            resolved.append(self.resolve_arg(arg))

        return resolved

class EthTools(Filtered, Preloaded):
    def __init__(self, server_address):
        self.server_address = server_address
        self.scope = str(uuid4())
        self.resolver = EthResolver(self)
        self.param_filter = {}

    @property
    def accounts(self):
        r = requests.get(self.server_address + "/accounts", headers={"Scope-Id": self.scope}, params=self.param_filter)
        self.clear_filter()

        r.raise_for_status()
        accounts = []

        for raw_account in r.json().get("items", []):
            accounts.append(Account.from_json(raw_account))
        return accounts

    @property
    def contract(self):
        r = requests.get(self.server_address + "/contracts", headers={"Scope-Id": self.scope}, params=self.param_filter)
        self.clear_filter()
        r.raise_for_status()
        contract = Contract.from_json(r.json())
        contract.instance = ConciseContract(w3.eth.contract(abi=contract.abi, address=contract.address))
        
        return contract

    def create_accounts(self, count=None, password=None, role=None):
        data = {}
        if role != None:
            data["role"] = role
        if count != None:
            data["count"] = count
        if password != None:
            data["password"] = password

        r = requests.post(self.server_address + "/accounts", headers={"Scope-Id": self.scope}, data=json.dumps(data))   
        r.raise_for_status()      

    def unlock(self):
        r = requests.get(self.server_address + "/accounts/unlock", headers={"Scope-Id": self.scope}, params=self.param_filter)
        self.clear_filter()
        r.raise_for_status()

    def deploy(self, name, sender, args=[]):
        data = {}
        data["abi"] = self.abi
        data["bin"] = self.bin
        data["name"] = name
        data["sender"] = sender
        data["args"] = args

        r = requests.post(self.server_address + "/contracts", headers={"Scope-Id": self.scope}, data=json.dumps(data))
        r.raise_for_status()

    def init_fixtures(self, path):
        with open(path) as f:
            fixtures = json.loads(f.read())

        workdir = fixtures.get("workdir", "")

        for account_description in fixtures.get("accounts", []):
            self.create_accounts(count=account_description.get("count"), role=account_description.get("role"))

        for contract_description in fixtures.get("contracts", []):
            contract_name = contract_description.get("name", "")
            sender = self.resolver.resolve_arg(contract_description.get("sender", ""))
            args = self.resolver.resolve_args(contract_description.get("args", []))

            abi_path = os.path.join(workdir, contract_description.get("abiPath", ""))
            bin_path = os.path.join(workdir, contract_description.get("binPath", ""))
            self.preload(abi_path, bin_path).deploy(contract_name, sender, args)

        for action_description in fixtures.get("postDeployActions", []):

            contract_name = action_description.get("contract", "")
            method = action_description.get("method", "")
            args = self.resolver.resolve_args(action_description.get("args", []))
            sender = self.resolver.resolve_arg(contract_description.get("sender", ""))
            isConstant = action_description.get("constant", False)
            
            contract = self.filter(name=contract_name).contract
            self.clear_filter()

            c = ConciseContract(w3.eth.contract(abi=contract.abi, address=contract.address))
            func = getattr(c, method)
            tx_receipt = None
            
            if isConstant:
                func(*args)
            else:
                while(tx_receipt is None):
                    tx_receipt = func(*args, transact={'from': sender})
                    

    def set_role_by_address(self, address, role):
        data = {}
        data["role" ] = role
        data["address"] = address
        r = requests.put(self.server_address + "/accounts", headers={"Scope-Id": self.scope}, data=json.dumps(data))
        r.raise_for_status()