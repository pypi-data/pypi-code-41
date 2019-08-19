from flask import make_response, redirect
from urllib.parse import urlparse

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from onelogin.saml2.constants import OneLogin_Saml2_Constants

from webplatform_backend.lib.responses import HttpResponseUnauthorized
from webplatform_auth.lib.session import SessionManager
# from webplatform_auth.lib import User

import json, os, sys

class Auth(object):
   def __init__(self, manager, settings, session_mgr):
      self.manager = manager
      self.settings = settings
      self.session_mgr = session_mgr

      base_path = settings.get_path()
      self.saml_config_file = base_path + "/docker/auth/saml/settings.json"
      self.saml_certs_path = base_path + "/docker/auth/saml"

   def prepare_saml_request(self, request):
      return {
         'http_host': request.host,
         'script_name': request.path,
         'server_port': request.headers['X-Nginx-Port'],
         'get_data': request.args.copy(),
         'post_data': request.form.copy()
      }

   def get_certs(self, settings):
      output = {
         "x509cert": "",
         "privateKey": ""
      }

      certs_files = [
         "%s/sp.crt" % self.saml_certs_path,
         "%s/sp.key" % self.saml_certs_path,
      ]

      for path in certs_files:
         with open(path) as target:
            file_data = ""
            for line in target:
               if "END" in line or "BEGIN" in line:
                  continue

               file_data += line.strip()

            if ".crt" in path:
               output['x509cert'] = file_data
            else:
               output['privateKey'] = file_data

      return output

   def setup_auth(self, request):
      saml_config = json.load(open(self.saml_config_file))

      protocol = request.headers['X-Forwarded-Proto']
      port = request.headers['X-Nginx-Port']
      host = request.headers['Host'].split(":")[0]

      if "X-Nodejs" in request.headers:
         if "0.0.0.0" in host:
            host = host.replace("0.0.0.0:8080", "localhost")
            if "X-Nodejs-Host" in request.headers:
               host = request.headers['X-Nodejs-Host']

      if port in host:
         base = (protocol, host)
         url = '%s://%s/auth/' % base
      else:
         if port == "443":
            base = (protocol, host)
            url = '%s://%s/auth/' % base
         else:
            base = (protocol, host, port)
            url = '%s://%s:%s/auth/' % base

      # saml_config['sp']['assertionConsumerService']['url'] = url

      if "wantAssertionsSigned" in saml_config['security'] and saml_config['security']['wantAssertionsSigned']:
         for key, value in self.get_certs(self.settings).items():
            saml_config['sp'][key] = value

      req = self.prepare_saml_request(request)
      auth = OneLogin_Saml2_Auth(req, saml_config)

      saml_settings = auth.get_settings()
      metadata = saml_settings.get_sp_metadata()
      errors = saml_settings.validate_metadata(metadata)
      if len(errors) > 0:
         print("Error found on Metadata: %s" % (', '.join(errors)))

      return auth

   def get(self, request):
      cookies = request.cookies

      protocol = request.headers['X-Forwarded-Proto']
      host = request.headers['HOST'].split(":")[0]
      port = request.headers['X-Nginx-Port']

      flask_settings = self.settings.get_config("flask")

      if "login" in cookies or "default-user" in flask_settings:
         if port != 443 or port != 80:
            base = (protocol, host, port)
            return_to = "%s://%s:%s/" % base
            return_to_url = request.args.get('q', False)
         else:
            base = (protocol, host)
            return_to = "%s://%s/" % base
            return_to_url = request.args.get('q', False)

         if return_to_url:
            return_to = return_to_url

         response = redirect(return_to)

         if "default-user" in flask_settings:
            uid = flask_settings['default-user']
            response.set_cookie("login", uid, max_age=86400)
         else:
            uid = cookies['login']

         # data = {
         #    "uid": uid,
         #    "is_auth": True,
         #    "redirect": False,
         # }

         # uid = data['uid']
         # data['user'] = self.manager.get_user(uid)
         # ip = request.remote_addr

         # session = self.manager.get_session(ip=ip, uid=uid)

         return response

      if "X-Nodejs" in request.headers:
         if "0.0.0.0" in host:
            host = request.headers['X-Nodejs-Host']

      if port != 443 or port != 80:
         base = (protocol, host, port)
         q = request.args.get('q', '%s://%s:%s/' % base)

         return_to = "%s://%s:%s/auth/" % base + "?q=%s" % (q)

         auth = self.setup_auth(request)
         response = auth.login(return_to=return_to)

         return redirect(response)

      else:
         base = (protocol, host)
         q = request.args.get('q', '%s://%s/' % base)

         return_to = "%s://%s/auth/" % base + "?q=%s" % (q)

         auth = self.setup_auth(request)
         response = auth.login(return_to=return_to)

         return redirect(response)

   def post(self, request):
      protocol = request.headers['X-Forwarded-Proto']
      host = request.headers['HOST'].split(":")[0]
      port = request.headers['X-Nginx-Port']
      ip = request.remote_addr
      
      if port != 443 or port != 80:
         base = (protocol, host, port)
         return_to = '%s://%s:%s/' % base
      else:
         base = (protocol, host)
         return_to = '%s://%s/' % base
      
      auth = self.setup_auth(request)
      auth.process_response()

      is_auth = auth.is_authenticated()
      response = auth.get_attributes()

      data = {}
      for key, value in response.items():
         if isinstance(value, list):
            if len(value) > 1:
               data[key] = value
            else:
               data[key] = value[0]
         else:
            data[key] = value

      if is_auth:
         uid = data['uid']
         q = request.args.get('q', return_to)

         session = self.session_mgr.find(uid=uid, ip=ip)
         
         if not session:
            self.session_mgr.create(uid=uid, ip=ip)

         if q:
            response = redirect(return_to)
            response.set_cookie("login", uid, max_age=86400)
            
            return response
         else:
            # data['user'] = self.manager.saml_auth(uid)
            # ip = request.remote_addr

            # session = self.manager.get_session(ip=ip, uid=uid)

            return_to = "/"
            if "RelayState" in request.form:
               return_to = request.form['RelayState']

            response = redirect(return_to, code=307)
            response.set_cookie("login", uid, max_age=86400)
            
            return response
      else:
         return HttpResponseUnauthorized(json.dumps({"message": "Error authenticated contact application admin."}))

   def metadata(self, request):
      auth = self.setup_auth(request)

      auth_settings = auth.get_settings()
      metadata = auth_settings.get_sp_metadata()

      errors = auth_settings.validate_metadata(metadata)

      if len(errors) == 0:
         resp = make_response(metadata, 200)
         resp.headers['Content-Type'] = 'text/xml'
      else:
         resp = make_response(', '.join(errors), 500)

      return resp