from pyftpdlib.authorizers import DummyAuthorizer
from lib.server.server_handler import TuyaHandler
from pyftpdlib.servers import FTPServer
# from lib.server.server-config import ServerConfig

from ..server.server_config import ServerConfig

class Sever:
    def __init__(self, config):
        self.config = config

    def start(self):
        self.config.showConfig()

        authorizer = DummyAuthorizer()
        authorizer.add_user('user', '12345', self.config.path, perm='elradfmwMT')
        authorizer.add_anonymous(self.config.path)

        handler = TuyaHandler
        handler.authorizer = authorizer

        server = FTPServer((self.config.address, self.config.port), handler)
        server.serve_forever()

