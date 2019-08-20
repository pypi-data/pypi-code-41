from pickle import dumps, loads
from pymemcache.client.base import Client

MemcacheClient = Client

def memcache_serializer(key, value):
    return dumps(value), 1

def memcache_deserializer(key, value, flags):
    return loads(value)

def create_memcache_client(host, port) -> MemcacheClient:
    return Client((host, port), serializer = memcache_serializer, deserializer = memcache_deserializer)
