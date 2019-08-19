import sys

app_path = "/home/cee-tools/api/"

if app_path not in sys.path:
   sys.path.append(app_path)

app_path = "/home/cee-tools/api/application/"

if app_path not in sys.path:
   sys.path.append(app_path)

from lib.utils.config import Settings

instance = "devel"
if len(sys.argv) > 1:
   instance = sys.argv[1]

settings = Settings(path="/home/cee-tools/", verify=False, instance=instance)

if __name__ == "__main__":
   from jobs.scheduler import Scheduler
   from lib.utils.modules import Modules
   from lib.utils.db import Manager

   p = Scheduler(settings)
   p.start()
   p.join()
