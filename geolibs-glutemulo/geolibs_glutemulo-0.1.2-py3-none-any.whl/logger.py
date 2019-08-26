
"""
Logging module
"""

import logging
from glutemulo.config import config

def init():
    """
    Initialize logger
    """
    logfmt = '[%(levelname)s][%(asctime)s][%(filename)s %(lineno)d] - %(message)s - '
    dtfmt = '%Y-%m-%d %I:%M:%S'
    logging.basicConfig(level=config.get('log_level', logging.INFO), format=logfmt, datefmt=dtfmt)

init()

log = logging.getLogger()
log.info('LOG started with level %s', log.level)
