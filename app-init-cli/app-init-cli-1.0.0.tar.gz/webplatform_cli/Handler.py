import os, sys, docker, json, shutil

class CLI(object):
   def __init__(self, settings, debug, force):
      self.settings = settings

      self.debug = debug
      self.force = force

      self.options = {
         "debug": self.debug,
         "force": self.force,
      }

      self.client = docker.DockerClient(base_url="unix://var/run/docker.sock")
      self.services = self.settings.get_service()
      self.base_path = settings.get_path()

   def parse_args(self, command, params):
      #only run setup and install, others have yet to be implemented 
      if command == "setup":
         method = getattr(self, command, None)()
     
      elif command == "config":
         method = getattr(self, command, None)(**params)
      
      elif command == "variables":
         self.parse_variables(**params)
      
      elif command == "apps":
         self.parse_apps(**params)
     
      elif command in ["start", "restart", "stop", "update", "reset"]:
         if len(params) > 0:
            for i in params:
               self.run_container(service=i, action=command)
         else:
            self.run_container(action=command)

   def run_container(self, service=None, action=None):
      from Docker import ContainerHandler
      
      container = ContainerHandler(self.settings, self.client, self.options)
      if service == None:
         container.run(action)
      else:
         container.run_service(service, action)

   def config(self, command, service, path=None, config=None, default=False):
      from lib.config import Settings
      
      if command in "get":
         config = self.settings.get_config(service)
         print(json.dumps(config, indent=2))
         sys.exit(1)
         
      
      try:
         if not default:
            if config == None:
               config = json.load(open(path))

      except IsADirectoryError:
         print("The value you specified for '--config' is a directory. This value but be a JSON file")
      except TypeError as e:
         print("The config you specified is not valid JSON")
      finally:
         config_path = "%s/settings/%s.json" % (self.base_path, service)
         default_path = "%s/settings/default-%s.json" % (self.base_path, service)
         
         config_target = open(config_path, "w")

         if not os.path.isfile(default_path):
            default_target = open(default_path, "w+")
            default_target.write(json.dumps(self.settings.get_config(service), indent=2))
            default_target.close()

         if not default:
            config_target.write(json.dumps(config, indent=2))
         else:
            config = json.load(open(default_path))
            config_target.write(json.dumps(config, indent=2))

         config_target.close()

      self.settings = Settings(path=self.base_path)

   def parse_variables(self, command=None, variable=None, value=None, default=False):
      config = self.settings.get_config("variables")

      current_value = self.settings.get_variable(variable)
      if current_value == None:
         sys.exit(1)

      if command == "get":
         print(current_value)
         sys.exit(1)

      if not default:
         if "," in value:
            config[variable] = value.strip().split(",")
         else:
            config[variable] = value

      self.config("set", "variables", config=config, default=default)
   
   def parse_apps(self, command=None, app=None, default=False):
      config = self.settings.get_config("variables")
      apps = self.settings.get_variable("applications")
      apps_path = self.settings.get_variable("apps-path")
      apps_configs = self.settings.get_variable("applications-configs")

      if len(apps) == 0 and command in ["list", "enable", "disable", "remove"]:
         print("Currently not tracking any applications.\nPlease add an application if you'd like to run '%s'" % command)
         sys.exit(1)

      if app in apps and command == "add":
         print("Application '%s' is currently already being tracked." % app)
         sys.exit(1)

      if command == "add":
         if "," in app:
            apps += app.strip().split(",")
         else:
            apps.append(app)

         app_config, error = self.settings.find_app(app)
         if error is not None:
            if error == "json parse error":
               print("Error parsing `app.json` for app `%s`" % app)
            elif error == "app no config":
               print("Application `%s` doesn't have a `app.json` file." % app)
            elif error == "no app dir":
               print("Application '%s' isn't a directory in `apps-path` (%s) variable." % (app, config['apps-path']))

            sys.exit(1)
         else:
            # Relative paths used in app.json configs.
            # Need to add those relative paths based on apps-path variable
            app_config['frontend']['path'] = os.path.join(apps_path, app, app_config['frontend']['path'])
            app_config['api']['path'] = os.path.join(apps_path, app, app_config['api']['path'])
            app_config['app-dir-name'] = app
            app_config['active'] = True
            apps_configs.append(app_config)

            self.parse_variables(command="set", variable="applications", value=apps)
            self.parse_variables(command="set", variable="applications-configs", value=apps_configs)

         print(",".join(apps))

      elif command == "list":
         print(",".join(current_value))
         sys.exit(1)
      
      elif command in ["enable", "disable"]:
         new_apps_configs = []
         for app_config in apps_configs:
            if app_config['app-dir-name'] == app:
               app_config['active'] = command == "enable"
            
            new_apps_configs.append(app_config)

         self.parse_variables(command="set", variable="applications-configs", value=new_apps_configs)

      elif command == "remove":
         if app not in apps:
            print("Application requested '%s' to remove doesn't exist" % app)
         else:
            new_apps_configs = [i for i in apps_configs if i['app-dir-name'] != app]
            new_apps = [i for i in apps if i != app]

            self.parse_variables(command="set", variable="applications", value=new_apps)
            self.parse_variables(command="set", variable="applications-configs", value=new_apps_configs)
   
   def setup(self):
      from tasks import build

      build.run("mongodb", force=self.options['force'])

   def tail(self, service, follow=False):
      pass