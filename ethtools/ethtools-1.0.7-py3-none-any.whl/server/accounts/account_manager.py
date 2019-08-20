import json
from threading import Lock
from ethtools.server.web_server import WebServer

class Account():
    def __init__(self):
        self.scope = 0
        self.address = ""
        self.password = ""
        self.role = ""

    def unlock(self):
        try:
            WebServer().w3.personal.unlockAccount(self.address, self.password) 
        except ValueError:
            return False,"Wrong password"
            
        return True, None
    
    def to_json(self):
        return {"address": self.address, "role": self.role}

class AccountStorage():
    def __init__(self):
        self.storage = {}
        self.mutex = Lock()

    def get_by_scope(self, scope):
        self.mutex.acquire()
        accounts = self.storage.get(scope, [])
        self.mutex.release()
        return accounts

    def get_by_address(self, address):
        self.mutex.acquire()
        for scope in self.storage:
            for account in self.storage[scope]:
                if account.address == address:
                    self.mutex.release()
                    return account
        self.mutex.release()
        return None

    def get_by_role(self, scope, role):
        self.mutex.acquire()
        accounts = []
        for account in self.storage.get(scope, []):
            if account.role == role:
                accounts.append(account)
        self.mutex.release()
        return accounts      

class AccountManager():
    def __init__(self):
        self.account_storage = AccountStorage()

    def unlock_by_address(self, address): 
        account = self.account_storage.get_by_address(address)

        if account is None:
            return False, "Wrong address"
        else:
            return account.unlock()
    
    def unlock_by_role(self, scope, role):
        for account in self.account_storage.get_by_role(scope, role):
            account.unlock()

        return "", None

    def get_accounts(self, scope):
        accounts = []
        for account in self.account_storage.get_by_scope(scope):
            accounts.append(account.to_json())
        return accounts

    def get_account_by_index(self, scope, index):  
        try:
            return self.account_storage.storage[scope][index], None
        except IndexError:
            return None, "Wrong index"
        except KeyError:
            return None, "Wrong scope"  

    def get_by_role(self, scope, role):
        accounts = []
        for account in self.account_storage.get_by_role(scope, role):
            accounts.append(account.to_json())
        return accounts

    def create_accounts(self, scope, password, count, role):
        for i in range(0, count):
            try:
                address = WebServer().w3.personal.newAccount(password)
                WebServer().w3.eth.sendTransaction({'to': address, 'from': WebServer().w3.eth.accounts[0], 'value': WebServer().config["balance"]})
            except ValueError:
                return False, "Wrong password"

            account = Account()
            account.scope = scope
            account.address = address
            account.password = password
            account.role = role

            if scope in self.account_storage.storage:
                self.account_storage.storage[scope].append(account)
            else:
                self.account_storage.storage[scope] = [account]


    def set_role_by_index(self, scope, index, role):
        account, err = self.get_account_by_index(scope, index)
        if err is None:
            account.role = role

        return err

    def set_role_by_address(self, scope, address, role):
        account = self.account_storage.get_by_address(address)

        if account is None:
            return "No account in storage"
        if account.scope != scope:
            return "Account does not belong this scope"

        account.role = role
        return None

    def delete_accounts(self, scope):
        try:
            del self.account_storage.storage[scope] 
        except KeyError:
            return False, "Wrong scope"

        return True, None

    def delete_account_by_index(self, scope, index):
        account, err = self.get_account_by_index(scope, index)
        if err is None:
            del account

        return err

    def delete_account_by_address(self, scope, address):
        account = self.account_storage.get_by_address(address)

        if account is None:
            return "No account in storage"
        if account.scope != scope:
            return "Account does not belong this scope"

        del account
        return None

