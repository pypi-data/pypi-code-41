
import json

from flask import Flask
from web3 import Web3, HTTPProvider

class WebServer:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(WebServer, cls).__new__(cls)
        return cls.instance

    def init(self, config_path):
        with open(config_path,'r') as f:
            self.config = json.loads(f.read())
        f.close()

        self.app = Flask(__name__)
        self.contract_manager = None
        self.account_manager = None

    def run(self):
        self.w3 = Web3(HTTPProvider(f'http://{self.config["node_address"]}:{self.config["node_port"]}/'))
        self.app.run(port=self.config["server_port"])
