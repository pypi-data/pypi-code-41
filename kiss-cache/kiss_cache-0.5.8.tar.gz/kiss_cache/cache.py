import base64
import logging
import threading
from typing import NewType, Callable, Tuple, Any, Dict, Optional, List

from kiss_cache.stores.in_memory import InMemoryStore

local = threading.local()
local.flush = False

logger = logging.getLogger(__name__)

DEFAULT_EXPIRATION_TIMEOUT = 60 * 10

KeyExtractor = NewType('KeyExtractor', Callable[[Tuple[Any, ...], Dict[str, Any], Callable[[Any], Any]], Any])


def default_key_extractor(func: Callable[[Any], str], *args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> str:
    key = func.__module__ + "." + func.__name__ + "." + str(args) + str(kwargs)
    key = key.encode()
    key = base64.b64encode(key)
    return key


def _extended_result(value: Any, is_from_cache: bool, extended_result: bool = False):
    return [value, {"is_from_cache": is_from_cache}] if extended_result else value


class Cache:

    def __init__(self, store=None,
                 key_extractor: KeyExtractor = default_key_extractor):
        self.store = store or InMemoryStore()
        self.key_extractor = key_extractor

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value, expire=DEFAULT_EXPIRATION_TIMEOUT):
        return self.store.set(key, value, expire)

    def memoize(self, expire=DEFAULT_EXPIRATION_TIMEOUT, excluded_keys: Optional[List[str]] = None,
                extended_result: bool = False):

        if excluded_keys is None:
            excluded_keys = []

        def decorator(func):
            def memoized_func(*args, flush: bool = False, **kwargs) -> Tuple[Any, bool]:

                if excluded_keys:
                    kwargs_for_key = {k: v for k, v in kwargs.items() if k not in excluded_keys}
                else:
                    kwargs_for_key = kwargs

                try:
                    key = self.key_extractor(func, *args, **kwargs_for_key)
                except Exception as e:
                    logger.exception(e)
                    return _extended_result(func(*args, **kwargs), False, extended_result=extended_result)

                flush: bool = flush and getattr(local, "flush", False)

                if flush is False:
                    value = self.get(key=key)
                else:
                    value = None

                if value is not None:
                    return _extended_result(value, True, extended_result=extended_result)

                value = func(*args, **kwargs)

                if value is not None:
                    self.set(key=key, value=value, expire=expire)

                return _extended_result(value, False, extended_result=extended_result)

            return memoized_func

        return decorator
