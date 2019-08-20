import json

class Context:
    def __init__(self, r):
        self.scope = r.headers.get("Scope-Id", 0)

        if r.data != b'':
            c = json.loads(r.data)
            self.password = c.get("password", "default")
            self.count = c.get("count", 1)
            self.role = c.get("role", "")
            self.address = c.get("address","")
        else:
            self.address = r.args.get("address")
            self.role = r.args.get("role")

    def __enter__(self):
       return self

    def __exit__(self, type, value, traceback):
        pass
