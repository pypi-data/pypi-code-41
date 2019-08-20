class Account:
    def __init__(self):
        self.address = ""
        self.role = ""

    @staticmethod
    def from_json(context):
        acc = Account()
        acc.address = context.get("address", "")
        acc.role = context.get("role", "")

        return acc

class Contract:
    def __init__(self):
        self.address = ""
        self.name = ""
        self.abi = ""

    @staticmethod
    def from_json(context):
        contract = Contract()
        contract.address = context.get("address", "")
        contract.name = context.get("name", "")
        contract.abi = context.get("abi", "")

        return contract