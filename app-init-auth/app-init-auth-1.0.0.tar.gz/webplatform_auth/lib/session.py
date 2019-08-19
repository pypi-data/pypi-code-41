from bson.objectid import ObjectId
from datetime import datetime, timedelta
import binascii, os

from webplatform_auth.lib.base_user import BaseUser

class SessionManager(object):
   __instance = None
   __session = None
   db = None
   settings = None
   apps = None
   user = None

   def __new__(cls, *args, **kwargs):
      if SessionManager.__instance is None:
         SessionManager.__instance = object.__new__(cls)

      return SessionManager.__instance
   
   def __init__(self, manager=None):
      if manager:
         self.db = manager.db("webplatform")
         self.settings = manager.settings
         self.apps = self.settings.list_applications()
         self.__session = None
         self.user = None

      else:
         self = SessionManager.__instance

   def get_user(self):
      return self.user.get_user()

   def get_uid(self):
      return self.user.get_uid()

   def set_user(self):
      if self.__session:
         self.user = BaseUser(self.__session, self.db)

   def set_session(self, session):
      self.__session = session
      self.set_user()

   def create(self, ip=None, uid=None):
      if ip and uid:
         if self.__session:
            setup = self.__session.setup(ip, uid)
         else:
            session = Session(self.db, ip=ip, uid=uid)
            setup = session.setup(ip, uid)

         self.db.sessions.insert_one(setup.doc)

         setup.session.permissions = self.get_permissions()

         self.__session = setup.session
         
         return self.get() 

   def update(self, session):
      expires = datetime.utcnow() + timedelta(hours=24)
      self.db.sessions.update({"_id": session.id}, {"$set": {"expires": expires}})

   def get(self):
      return self.__session

   def find(self, **kwargs):
      session = Session(self.db, **kwargs)
      check = session.get()

      now = datetime.utcnow()
      if check and now > check.expires:
         self.delete(check)
         
         return None
   
      return check

   def delete(self, session):
      self.db.sessions.remove({"_id": session.id})
      
   def validate(self, token):
      if token:
         uid = self.db.users.find_one({"token": token}, {"uid": 1})

         if uid:
            return True

      return False

   def get_permissions(self):
      if self.__session:
         cursor = self.db.permissions.find({"uid": self.__session.uid})

         if cursor == None:
            cursor = self.__set_default_user_permissions(self.__session.uid)

         output = {}
         for i in cursor:
            output[i['application']] = i['permissions']

         return output
      
      return None

   def __set_default_user_permissions(self, uid):
      documents = [
         {
            "name": "system",
            "permissions": [],
            "uid": uid
         }
      ]
      for app in self.apps:
         d = {
            "permissions": [],
            "application": app['name'],
            "uid": uid
         }
         documents.append(d)

      self.db.permissions.insert_one(documents)
      return documents

class Session(object):
   def __init__(self, db, ip=None, uid=None, token=None):
      self.db = db
      self.__session = None
      self.__token = None
      
      session = None
      
      if token != None:
         session = self.db.sessions.find_one({"token": token, "ip": ip})
         
      else:
         has_session = self.db.sessions.find_one({"uid": uid}, {"uid": 1, "token": 1})
         if has_session:
            self.__token = has_session['token']

         if uid != None and ip != None:
            session = self.db.sessions.find_one({"uid": uid, "ip": ip})

         elif uid != None and ip == None:
            session = []
            cursor = self.db.sessions.find({"uid": uid})
            for i in cursor:
               session.append(i)

      if session:
         if isinstance(session, list):
            self.__session = [self.__parse_cursor(i) for i in session]

         self.__session = self.__parse_cursor(session)

   def get_all_sessions(self):
      if self.__session:
         cursor = self.db.sessions.find({"uid": self.__session.uid})
         return [self.__parse_cursor(i) for i in cursor]

      return []

   def get(self):
      return self.__session

   def __dir__(self):
      return ["uid", "token", "expires", "ip"]

   def __parse_cursor(self, obj):
      for key, value in obj.items():
         if key == '_id':
            setattr(self, "id", value)
         else:
            setattr(self, key, value)

      return self

   def setup(self, ip, uid):
      token = self.__token
      if not token:
         token = self.gen_token()

      doc = {
         "_id": ObjectId(),
         "expires": datetime.utcnow() + timedelta(hours=24),
         "token": token,
         "ip": ip,
         "uid": uid,
      }

      session = self.__parse_cursor(doc)
      output = {
         "doc": doc, 
         "session": session
      }

      return self.__parse_cursor(output)

   def gen_token(self, n=8):
      return binascii.hexlify(os.urandom(n)).decode('UTF-8')
