import redis
import json
import time


class RedisBackend:
    def __init__(self, expires_seconds, key_prefix="gluto:", **redis_conf):
        self.expires_seconds = expires_seconds
        self.key_prefix = key_prefix
        # self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.redis = redis.StrictRedis(**redis_conf)

    def consume(self, messages):
        for msg in messages:
            key = self.key_prefix + str(time.time())
            self.redis.set(key, json.dumps(msg), ex=self.expires_seconds)
