import logging
import threading

try:
    from gunicorn.glogging import Logger as _Logger
except ImportError:
    _Logger = None
