from webplatform_cli.lib.db import Manager
from webplatform_auth.lib.permissions import PermissionManager

class BaseUser:
   def __init__(self, session, db):
      self.db = db
      self.uid = session.uid
      self.session = session
      self.permissions_mgr = PermissionManager(session)

   def get_uid(self):
      return self.uid

   def get_sessions(self):
      return self.session.get_all_sessions()

   def get_picture_url(self, email):
      email = email.encode('utf-8')
      return "https://secure.gravatar.com/avatar/" + hashlib.md5(email).hexdigest() + "?s=100&d=identicon"

   # def set_permissions(self, permissions):
   #    self.permissions = permissions

   # def get_permissions(self, app=None):
   #    if app == None:
   #       return self.permissions
   #    else:
   #       if app in self.permissions:
   #          return self.permissions[app]
   #       else:
   #          return []

   # def get_session(self, **kwargs):
   #    return self.session.get_session(**kwargs)

   # def get_all_sessions(self, uid):
   #    return self.session.get_session(uid=uid)

   # def validate_session(self, *args):
   #    return self.session.validate(*args)

   def get_user(self):
      sessions = self.session.get_all_sessions()
      permissions = self.permissions_mgr.list_user_permissions()
      # settings = get_settings.call(uid=kwargs['kerberos'], output="uid")
      token = self.session.token

      return {
         "sessions": sessions,
         "permissions": permissions,
         # "settings": settings,
         "token": token,
         "uid": self.uid,
      }

   def set_user(self):
      pass
