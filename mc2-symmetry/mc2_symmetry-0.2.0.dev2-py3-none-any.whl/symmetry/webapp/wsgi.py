import logging
import os

import falcon
import pymq
import redis
from falcon_cors import CORS
from falcon_multipart.middleware import MultipartMiddleware
from pymq.provider.redis import RedisConfig

from symmetry.webapp.app import setup, DefaultRedisContext

logger = logging.getLogger(__name__)


def create_context():
    rds = redis.Redis(os.getenv('symmetry_redis_host', 'localhost'), decode_responses=True)
    pymq.init(RedisConfig(rds))
    return DefaultRedisContext(rds)


cors = CORS(allow_origins_list=['http://localhost:63342'])
api = falcon.API(middleware=[cors.middleware, MultipartMiddleware()])
setup(api, create_context())
