# coding: utf-8
"""
from redis.lock import Lock
from django_pie.redis import get_redis, redis_key

rds = get_redis('test')

key = redis_key('a', 'b', 'c')  # generate 'a:b:c'

# lock
with Lock(key, timeout=60, blocking_timeout=1).acquire() as lock:
    if lock:
        # get lock
    else:
        # do not get lock

# keys
rds.exists(key)
rds.expire(key, seconds)
rds.delete(key)

# strings
rds.set(key, value, ex=seconds)
rds.get(key)
rds.incrby(key, amount=1)
rds.decrby(key, amount=1)

# sets
rds.sadd(key, member)
rds.smembers(key)
rds.scard(key)
rds.sismember(key, member)
rds.srem(key, member)
rds.spop(key)

# hash
rds.hget(name, key)
rds.hset(name, key, value)
rds.hdel(name, key)
rds.hexists(name, key)
rds.hincrby(name, key, amount)
rds.hlen(name)
rds.hincrbyfloat(name, key, amount)

# lists
rds.llen(name)
rds.lpush(name, value)
rds.lpop(name)
rds.rpush(name, value)
rds.rpop(name)

# sorted sets
rds.zadd(name, mapping)
rds.zincrby(name, key, amount)
rds.zcard(name)
rds.zrank(name, value)
rds.zrem(name, key)
rds.zrange(name, start, end, withscores=True)
rds.zrevrange(name, start, end, withscores=True)

# pipeline
pipe = rds.pipeline()
pipe.set(key, value)
pipe.get(key)
result = pipe.execute()  # result is list

"""
from redis import Redis
from django.conf import settings


class RedisException(Exception):
    pass


def get_redis(name='default'):
    conf = settings.REDIS_CONF[name]
    if conf.get('decode_responses') is None:
        raise RedisException('decode_responses should be declared in redis conf')
    return Redis(**conf)


def redis_key(*args):
    return ':'.join([str(arg) for arg in args])
