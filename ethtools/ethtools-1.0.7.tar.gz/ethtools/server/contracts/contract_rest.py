import json

from flask import request
from flask.views import MethodView

from ethtools.server.web_server import WebServer
from .contract_manager import ContractManager
from .contract_context import Context

def register_rest_api():
    WebServer().contract_manager = ContractManager()
    WebServer().app.add_url_rule("/contracts", view_func=ContractsHandler.as_view("contracts"))

class ContractsHandler(MethodView):
    def get(self):
        with Context(request) as c:
            response = WebServer().contract_manager.get_contract(c.scope, c.name)
            
        return response, 200

    def post(self):
        with Context(request) as c:
            WebServer().account_manager.unlock_by_address(c.sender)
            response = WebServer().contract_manager.create_contract(c.scope, c.name, c.sender, c.abi, c.bytecode, c.args)
        return response, 200