class ServerConfig:
    def __init__(self, path, address, port):
        self.port = port
        self.path = path
        self.address = address

    def showConfig(self):
        print("Server start at ", self.address,
              " at path ", self.path,
              " at port", self.port)