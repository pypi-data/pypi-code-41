from __future__ import annotations

from abc import ABC
from typing import *

T = TypeVar('T')
R = TypeVar('R')
K = TypeVar('K', bound='Monad')
class Functor(Generic[K, T], ABC):
    def map(self, f: Callable[[T], R]) -> K[R]:
        raise NotImplementedError

class Monad(Generic[K, T], ABC):
    def flat_map(self, f: Callable[[T], K[R]]) -> K[R]:
        raise NotImplementedError
    @property
    def flatten(self) -> T:
        raise NotImplementedError


__all__ = \
[
    'Monad',
    'Functor',
]
