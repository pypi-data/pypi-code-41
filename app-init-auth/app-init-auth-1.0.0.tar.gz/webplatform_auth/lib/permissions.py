from webplatform_cli.lib.db import Manager

class PermissionManager(object):
   def __init__(self, session):
      self.manager = Manager()
      self.db = self.manager.db('webplatform') 
      self.session = session
      # self.settings = settings

   def get_application_uids(self, application, permission):
      app = PermissionsApplication(self.db, application)
      return app.get_uids(permission)

   def list_user_permissions(self):
      user = PermissionsUser(self.db, self.session.uid)
      return user.list_permissions()

   def get_application(self, app=None):
      permissions = self.list_user_permissions()
      
      if app == None:
         return permissions
      else:
         if app in permissions:
            return permissions[app]
         else:
            return []
   
class Permission(object):
   def __init__(self):
      pass

class PermissionsApplication(object):
   def __init__(self, db, application):
      self.application = application
      self.db = db

   # users.permissions.get
   def get_uids(permission):
      pipeline = [
         { "$match": {"application": self.application}},
         { "$unwind": "$permissions" },
         { "$group":
            {
               "_id": "$permissions",
               "uids": {
                  "$addToSet": "$uid",
               },
            }
         },
         { "$match":
            {
               "_id": permission,
            }
         },
      ]

      cursor = self.db.permissions.aggregate(pipeline)

      if cursor != None:
         for i in cursor:
            return i['uids']

      return None

   # permissions.applications.add
   def add(self, uid, permission):
      cursor = self.db.permissions.find_one({
         "application": self.application,
         "uid": uid,
      })

      if cursor is None:
         add_user.call(uid=uid, application=self.application)

      self.db.permissions.update(
         {
            "application": self.application,
            "uid": kwargs["uid"]
         },
         {
            "$push": {
               "permissions": permission
            }
         }
      )

      return get_application.call(application=self.application)

class PermissionsUser(object):
   def __init__(self, db, uid):
      self.uid = uid
      self.db = db
      self.manager = Manager()

   def list_permissions(self):
      permissions = {}

      apps = self.manager.get_application()
      apps.append({"name": "system"})
      for app in apps:

         if app['name'] != "system":
            list_name = app['api']['name'].split("_")
            camel_case = ''.join([list_name[x].title() for x in range(1, len(list_name))])
            name = list_name[0] + camel_case
         else:
            name = app['name']

         permissions[name] = {}

         all_permissions = self.db.permissions.find({"application": app['name']}).distinct("permissions")

         user_permissions = self.db.permissions.find_one({"uid": self.uid, "application": app['name']})

         if user_permissions != None:
            all_true = False
            if user_permissions['application'] == app['name']:
               all_true = "admin" in user_permissions['permissions']

            for p in user_permissions['permissions']:
               key = 'is_' + p
               if all_true:
                  permissions[name][key] = True
               elif p in all_permissions:
                  permissions[name][key] = True
               else:
                  permissions[name][key] = False

      return permissions

class PermissionsModule(object):
   def __init__(self):
      pass