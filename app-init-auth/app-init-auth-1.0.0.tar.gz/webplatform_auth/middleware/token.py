from querystring_parser import parser
import json, os

from webplatform_auth.lib.session import SessionManager

def process_request(session_mgr, request=None, response=None):
   ip = request.remote_addr
   token = None
   uid = None
   
   token = find(request)
   check = session_mgr.validate(token)
   
   if check:
      session_mgr.set_session(check)

   else:
      uid = request.cookies.get('login', False)

      if uid:
         session = session_mgr.find(uid=uid, ip=ip)

         if session:
            session_mgr.set_session(session)
         else:
            session_mgr.create(uid=uid, ip=ip)
         
         user = session_mgr.get_user()

def find(request):
   token = None
   if request.headers.get("token", False):
      token = request.headers.get('token')

   elif request.method == "POST":
      if request.data != b'':
         if b'SAML' not in request.data:
            data = json.loads(request.data)
            if "token" in data:
               token = data['token']
      else:
         token = request.form.get("token")

   elif request.method == "GET":
      url = request.full_path.split("?")[1:]
      args = parser.parse("&".join(url))
      token = args.get("token", None)

   return token
