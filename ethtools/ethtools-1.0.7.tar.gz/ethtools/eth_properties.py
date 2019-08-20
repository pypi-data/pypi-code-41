import json

class Filtered:
    param_filter = {}

    def filter(self, role=None, address=None, name=None):
        if role != None:
            self.param_filter["role"] = role
        if address != None:
            self.param_filter["address"] = address
        if name != None:
            self.param_filter["name"] = name

        return self

    def clear_filter(self):
        self.param_filter = {}

class Preloaded:
    abi = ""
    bin = ""

    def preload(self, abi_path, bin_path):
        with open(abi_path) as abi_f:
            self.abi = json.loads(abi_f.read())
        with open(bin_path) as bin_f:
            self.bin = bin_f.read()

        return self
