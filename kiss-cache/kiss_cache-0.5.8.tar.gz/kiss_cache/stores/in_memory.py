from time import time
from typing import Dict, Any


class InMemoryPackage:
    __slots__ = ['value', 'expired']

    def __init__(self, value: Any, expired: float):
        self.value = value
        self.expired = expired


class InMemoryStore:

    def __init__(self):
        self.store: Dict[str, InMemoryPackage] = {}

    def get(self, key: str):
        package = self.store.get(key)

        if package is None:
            return None

        if time() > package.expired:
            self.store.pop(key)
            return None

        return package.value

    def set(self, key: str, value: Any, expire):

        package = InMemoryPackage(value=value, expired=time() + expire)

        self.store[key] = package
        return True
