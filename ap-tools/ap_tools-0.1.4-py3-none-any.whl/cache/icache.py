from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar('T')

class ICache(ABC):
    @abstractmethod
    def get(self, key: str, default: T=None) -> T:
        pass

    @abstractmethod
    def put(self, key: str, value: T, ttl: int=None):
        pass

    @abstractmethod
    def clear(self, query: str=None):
        pass
