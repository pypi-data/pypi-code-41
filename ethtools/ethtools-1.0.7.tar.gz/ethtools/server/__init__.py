import sys
from threading import Thread

from .web_server import WebServer
from .accounts import register_rest_api as accounts_rest
from .contracts import register_rest_api as contracts_rest

class EthServer:
    def __init__(self, config_path):
        webserver = WebServer()
        webserver.init(config_path)
        accounts_rest()
        contracts_rest()
        
        t = Thread(target=webserver.run)
        t.setDaemon(True)
        t.start()