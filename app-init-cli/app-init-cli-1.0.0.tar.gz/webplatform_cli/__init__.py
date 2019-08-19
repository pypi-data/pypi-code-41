import os, sys

controller_path = os.path.dirname(os.path.realpath(__file__))
base_path = os.path.abspath(os.path.join(controller_path))

if base_path not in sys.path:
   sys.path.append(base_path)

if controller_path not in sys.path:
   sys.path.append(controller_path)

# import webplatform_backend as backend
# from .containers import *
from .lib.config import Settings
from .lib.db import Manager
from .cli import main 
# from .tasks import *
# from .cli import Docker
# from .handler import ContainerHandler
