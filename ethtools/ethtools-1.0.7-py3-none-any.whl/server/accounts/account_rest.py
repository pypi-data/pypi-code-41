import json

from flask import request
from flask.views import MethodView

from ethtools.server.web_server import WebServer
from .account_manager import AccountManager
from .account_context import Context

def register_rest_api():
    WebServer().account_manager = AccountManager()
    WebServer().app.add_url_rule("/accounts", view_func=AccountsHandler.as_view("accounts"))
    WebServer().app.add_url_rule("/accounts/unlock", view_func=UnlockHandler.as_view("accounts/unlock"))

class AccountsHandler(MethodView):
    def get(self):
        with Context(request) as c:
            if c.address is not None:
                account = WebServer().account_manager.account_storage.get_by_address(c.address)
                if account != None:
                    response = {"items":[account.to_json()]}
                    return response, 200
                else:
                    return {}
            if c.role != None:
                accounts = WebServer().account_manager.get_by_role(c.scope,c.role)
                return {"items": accounts}, 200

            response = {"items": WebServer().account_manager.get_accounts(c.scope)}
        return response, 200

    def post(self):
        with Context(request) as c:
            account = WebServer().account_manager.create_accounts(c.scope, c.password, c.count, c.role)  
        return "OK", 204

    def put(self):
        with Context(request) as c:
            err = WebServer().account_manager.set_role_by_address(c.scope, c.address, c.role)
        if err is not None:
            return err, 400
        else:
            return "OK", 204
                    
                    
class UnlockHandler(MethodView):
    def get(self):
        with Context(request) as c:
            if c.address != None:
                _, err = WebServer().account_manager.unlock_by_address(c.address)
            if c.role != None:
                _, err = WebServer().account_manager.unlock_by_role(c.scope, c.role)
            if err is not None:
                return err, 400
            else:
                return "OK", 204
            