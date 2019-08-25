from cachetools import Cache, LFUCache, LRUCache, RRCache, TTLCache, cached


def make_dict_cache():
    return {}


def make_LFU(maxsize=128):
    return LFUCache(maxsize)


def make_LRU(maxsize=128):
    return LRUCache(maxsize)


def make_RR(maxsize=128):
    return RRCache(maxsize)


def make_TTL(ttl_min: float, maxsize=128):
    return TTLCache(maxsize, ttl=ttl_min * 60)


class ActionCache(TTLCache):
    """
    Overriding this class and then overriding the action method allows a developer to use this as a TTL cache with a
       middleware style translation piece. For example, cache a key and it will execute action with that key to get
       some value
    """

    def __init__(self, ttl_min: float, maxsize=128):
        super().__init__(maxsize, ttl=ttl_min * 60)

    def __missing__(self, key):
        value = self.action(key)
        self[key] = value
        return value

    def action(self, key):
        return None
