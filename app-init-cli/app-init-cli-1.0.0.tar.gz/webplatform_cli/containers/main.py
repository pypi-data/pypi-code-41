from lib.config import Settings
import socket

settings = Settings()
base_path = settings.get_path()

volumes = {
   # "%s/application" % base_path: {
   #    "bind": "/home/cee-tools/setup",
   #    "mode": "rw",
   # },
}

def add_volumes(add):
   tmp = volumes
   for key, value in add.items():
      tmp[key] = value
   return tmp

def get_environment(service):
   return {
      #doesn't work on mac
      # "HOST_MACHINE": socket.gethostbyname(socket.gethostname()),
      "WEBPLATFORM_SERVICE": service,
   }
