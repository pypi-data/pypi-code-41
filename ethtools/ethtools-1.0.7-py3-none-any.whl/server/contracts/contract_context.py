import json

class Context:
    def __init__(self, r):
        self.scope = r.headers.get("Scope-Id", 0)

        if r.data != b'':
            c = json.loads(r.data)
            self.sender = c.get("sender", "")
            self.bytecode = c.get("bin", "")
            self.args = c.get("args", [])
            self.name = c.get("name", "")
            self.abi = c.get("abi", "") 
        else:
            self.name = r.args.get("name", "")

    def __enter__(self):
       return self

    def __exit__(self, type, value, traceback):
        pass