from lib.config import Settings
from docopt import docopt
import os, sys, json

settings = Settings()
config = settings.get_config("cli")
services = settings.get_config("variables")['services']

def config(command, argv):
   valid_args = sorted(services + ["cli"])
   args_doc = '\n   '.join(valid_args)
   doc = """usage: 
   webplatform-cli <command> <service> --path <path>
   webplatform-cli <command> <service> --default
   webplatform-cli <command> [<service>]

commands allowed on config (all commands a service must be specified)
   set       Set the config file to be used for a given service.
             The --path argument is required.
             You can also specify --default to reset all the config files

   get       Get the data in specified service config

the following are valid services with configs:
   %s
""" % args_doc
   
   args = docopt(doc, argv=argv)

   if args['<command>'] == 'set' and not args['--path'] and not args['--default']:
      sys.stderr.write(doc)
      sys.exit(1)

   # if args['--config']:
   #    args['<config>'] = os.path.abspath(os.path.join(settings.get_path(), args['<config>']))
   
   return args

def variables(command, argv):
   doc = """usage: 
   webplatform-cli variables set <variable-key> <value>
   webplatform-cli variables get <variable-key>
   webplatform-cli variables get

list of variables you have access to get and set
   apps-path         Directory where applications are stored.
                     Default value is /home/$user/
   services          Allow for services to be specified in cli config
"""

   argv.insert(0, command)
   args = docopt(doc, argv=argv)

   return args

def apps(command, argv):
   doc = """usage: 
   webplatform-cli apps <app-command> <app-name>
   webplatform-cli apps <app-command>

list of commands to be run against apps
   add               Add an application to webplatform.
                     Configuation will be checked and a valid `apps-path variable needs to be set
   remove            Remove an app from webplatform
   enable            Enable an app after it's been disabled
   disable           Disable an app to be bundle in with backend and frontend services
   list              List all application webplatform is currently tracking
"""

   argv.insert(0, command)
   args = docopt(doc, argv=argv)

   if args['<app-command>'] not in ["add", "remove", "enable", "disable", "list"]:
      sys.stderr.write(doc)
      sys.exit(1)

   return args

def service(command, argv):
   argv.insert(0, command)
   valid_args = set(services)
   args_doc = '\n   '.join(sorted(valid_args))
   doc = """usage:
   webplatform-ctl [options] %s [<args>...]

options:
   -h --help     Print this help message

%s the following processies:
   %s
""" % (command, command, args_doc)

   args = docopt(doc, argv=argv)
   if valid_args.issuperset(args['<args>']):
      return args
   else:
      sys.stderr.write(doc)
      sys.exit(1)

def noargs(command, argv):
   argv.insert(0,command)
   doc = """usage:
   webplatform-ctl [options] %s

options:
   -h --help     Print this help message
""" % (command,)
   return docopt(doc,argv=argv)

   return docopt(doc, argv=argv)

def parser(command, args, debug=False, force=False):
   ctrl = {
      "command": command
   }
   kwargs = None

   if command in ['start', 'restart', 'stop', 'reset']:
      subargs = service(command, args)
   elif command == 'setup':
      subargs = noargs(command, args)
   elif command == 'config':
      subargs = config(command, args)
   elif command == 'variables':
      subargs = variables(command, args)
   elif command == 'apps':
      subargs = apps(command, args)

   if debug:
      print(args)
      print(subargs)       

   if command == 'setup':
      ctrl['params'] = []

   elif command == 'config':
      kwargs = {
         "command": subargs['<command>'], 
         "service": subargs['<service>']
      }

      if subargs['--path']:
         kwargs['path'] = subargs['<path>']

      if subargs['--default']:
         kwargs['default'] = subargs['--default']
   
   elif "set" in subargs or "get" in subargs:
      kwargs = {
         "variable": subargs['<variable-key>'],
      }

      if subargs['set']:
         kwargs['command'] = "set"
      else:
         kwargs['command'] = "get"

      if "<value>" in subargs:
         kwargs['value'] = subargs['<value>']

   elif command == 'apps':
      kwargs = {
         'command': subargs['<app-command>'],
         'app': None,
      }
      
      if subargs['<app-command>'] in ["add", "remove", "enable", "disable"]:
         kwargs['app'] = subargs['<app-name>']

   else:
      ctrl['params'] = subargs['<args>']

   if debug:
      print(json.dumps(ctrl, indent=2))

   if kwargs is not None:
      ctrl['params'] = kwargs 
   
   return ctrl