#!/bin/python3

# preventing __pycache__ from being created
import os, sys, json
sys.dont_write_bytecode = True

container_path = "/home/container/webplatform_cli"
controller_path = os.path.dirname(os.path.realpath(__file__))
base_path = os.path.abspath(os.path.join(controller_path))
settings_path = base_path

if os.path.isdir(container_path):
   if container_path not in sys.path:
      sys.path.append(container_path)
   
   settings_path = container_path
else:
   settings_path = os.path.abspath(os.path.join(controller_path, '../container/'))

if base_path not in sys.path:
   sys.path.append(base_path)

from flask import Flask, redirect, make_response, send_file, request

if controller_path not in sys.path:
   sys.path.append(base_path)

from views.saml import Auth
from webplatform_auth.middleware import token
from webplatform_auth.lib import SessionManager

from webplatform_cli.lib.config import Settings
from webplatform_cli.lib.db import Manager

from webplatform_backend.lib.responses import HttpResponse, HttpResponseBadRequest, HttpResponseInternalServerError

manager = Manager()
settings = Settings(path=settings_path, verify=False)
session_mgr = SessionManager(manager)

auth = Auth(manager, settings, session_mgr)

app = Flask(__name__)

app.url_map.strict_slashes = False

@app.before_request
def token_before():
   token.process_request(session_mgr, request=request)

# @app.after_request
# def token_after(response):
#    token.process_request(session_mgr, request=request, response=response)

#    return response

@app.route("/auth", methods=['POST', 'GET'])
def saml_auth():
   if request.method == 'GET':
      return auth.get(request)
   else:
      return auth.post(request)

# @app.route("/metadata")
# def metadata():
#    protocol = request.headers['X-Forwarded-Proto']
#    port = request.headers['X-Nginx-Port']
#    host = request.headers['Host'].split(":")[0]

#    if "X-Nodejs" in request.headers:
#       if "0.0.0.0" in host:
#          host = host.replace("0.0.0.0:8080", "localhost")
#          if "X-Nodejs-Host" in request.headers:
#             host = request.headers['X-Nodejs-Host']

#    if port in host:
#       base = (protocol, host)
#       url = '%s://%s/callback/' % base
#    else:
#       base = (protocol, host, port)
#       url = '%s://%s:%s/callback/' % base

#    if len(request.args) > 0:
#       is_config = request.args.get("config", False)
#       if is_config:
#          config_file = open(settings.get_config("flask")['saml-settings'] + "/saml.json")
#          config = json.load(config_file)
#          config['sp']['assertionConsumerService']['url'] = url
#          config_file.close()

#          config_file = open(settings.get_config("flask")['saml-settings'] + "/saml-advanced.json")
#          advanced_config = json.load(config_file)
#          config_file.close()

#          return HttpResponse(json.dumps({"config": config, "advanced": advanced_config}, indent=2))

#    return saml.metadata(request)