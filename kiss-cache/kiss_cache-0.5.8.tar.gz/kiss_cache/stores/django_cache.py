import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)


def default_serialize(value: Any) -> str:
    return value


def default_deserialize(value: str) -> Any:
    return value


class DjangoCacheStore:

    def __init__(self, cache_identifier='default',
                 serialize: Callable[[Any], str] = default_serialize,
                 deserialize: Callable[[str], Any] = default_deserialize):

        try:
            from django.core.cache import caches
        except ImportError:
            raise ImportError('Django required for this cache store')

        self.cache = caches[cache_identifier]
        self.serialize = serialize
        self.deserialize = deserialize

    def get(self, key):

        try:
            value = self.cache.get(key)

            if value is None:
                return None

            return self.deserialize(value)

        except Exception as e:
            logger.exception(e)
            return None

    def set(self, key, value, expire):
        try:
            value = self.serialize(value)
            return self.cache.set(key, value, expire)
        except Exception as e:
            logger.exception(e)
