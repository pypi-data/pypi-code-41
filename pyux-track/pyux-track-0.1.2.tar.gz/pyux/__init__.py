import os.path as path
from datetime import datetime

__LOGGING_CONFIG__ = path.join(path.dirname(path.abspath(__file__)), 'logging.conf')
__LAUNCH_TIME__ = datetime.now()
