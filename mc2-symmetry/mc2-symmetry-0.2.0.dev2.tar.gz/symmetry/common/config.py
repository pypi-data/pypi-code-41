import logging
import os

import redis

logger = logging.getLogger(__name__)


def guess_root_path():
    if 'etc' in os.listdir(os.path.curdir):
        return os.path.abspath(os.path.curdir)

    if 'etc' in os.listdir('../..'):
        return os.path.abspath('../..')

    if 'etc' in os.listdir('..'):
        return os.path.abspath('..')

    raise ValueError('Did not find root directory with etc dir')


def get_nodes_config():
    path = os.getenv('symmetry_nodes_ini')

    if not path:
        path = os.path.join(guess_root_path(), 'etc', 'nodes.ini')

    if not os.path.isfile(path):
        logger.warning('path to nodes in %s is not a file', path)

    return path


def get_redis():
    return redis.Redis(
        host=os.getenv('symmetry_redis_host', 'localhost'),
        port=int(os.getenv('symmetry_redis_port', 6379)),
        decode_responses=True
    )
