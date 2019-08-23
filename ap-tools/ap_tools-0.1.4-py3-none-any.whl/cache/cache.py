import time
from dataclasses import dataclass
from typing import Any, TypeVar
import re
from .icache import ICache

T = TypeVar('T')

class Cache(ICache):
    _data = {}
    DEFAULT_TTL = 15

    @dataclass
    class CacheObject:
        __slots__ = ['key', 'value', 'expiry']
        key: str
        value: T
        expiry: int

    @staticmethod
    def put(key: str, value: T, ttl: int=None):
        if ttl is None:
            ttl = Cache.DEFAULT_TTL

        Cache._data[key] = Cache.CacheObject(key, value, time.time() + ttl)

    @staticmethod
    def get(key: str, default: T=None) -> T:
        Cache._expire(key)

        rs = Cache._data.get(key, default)
        return rs if not isinstance(rs, Cache.CacheObject) else rs.value

    @staticmethod
    def clear(query=None):
        if query is None:
            Cache._data = {}
        else:
            pattern = re.compile(query)
            deletions = set()
            for key in Cache._data:
                if pattern.match(key):
                    deletions.add(key)

            for key in deletions:
                del Cache._data[key]

    @staticmethod
    def _expire(key: str):
        now = time.time()
        if key in Cache._data and Cache._data[key].expiry < now:
            del Cache._data[key]
