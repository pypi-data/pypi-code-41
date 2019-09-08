from __future__ import annotations

from dataclasses import dataclass
from typing import *

from .containers import *
from .monads import *
from .predef import *

class EmptyOption(ValueError):
    pass

T = TypeVar('T')
R = TypeVar('R')
K = TypeVar('K', bound='Monad')
@dataclass(frozen=True, repr=False)
class Option(Container['Option[T]', T], Monad['Option[T]', T], Functor['Option[T]', T], Generic[T]):
    value: Optional[T]
    
    #region Properties
    @property
    def is_defined(self) -> bool:
        return not self.is_empty
    
    @property
    def is_empty(self) -> bool:
        return self.value is None
    
    @property
    def non_empty(self) -> bool:
        return self.is_defined
    
    @property
    def get(self) -> T:
        if (self.is_empty):
            raise EmptyOption("Could not get from empty Option")
        else:
            return self.value
    
    @property
    def flatten(self) -> T:
        return self.flat_map(identity)
    #endregion
    
    #region Methods
    def get_or_else(self, orElse: T) -> T:
        return self.value if (self.is_defined) else orElse
    
    def map(self, f: Callable[[T], R]) -> 'Option[R]':
        return self.flat_map(lambda x: Option(f(x)))
    
    def flat_map(self, f: Callable[[T], 'Option[R]']) -> 'Option[R]':
        if (self.is_defined):
            return f(self.value)
        else:
            return Option.empty
    
    def foreach(self, f: Callable[[T], Any]):
        self.map(f)
    #endregion
    
    def __repr__(self):
        if (self.is_defined):
            return f"Some({repr(self.value)})"
        else:
            return "None"
    
    def __bool__(self) -> bool:
        return self.is_defined
    
    def __len__(self):
        return int(self.is_defined)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def __iter__(self):
        if (self.is_defined):
            yield self.value

@dataclass(frozen=True, repr=False)
class _SomeNone(Option[T], Generic[T]):
    value: Optional[T] = None
    
    @property
    def is_empty(self) -> bool:
        return False

Option.empty = Option(None)
_some_empty_option = _SomeNone()
def Some(value: T) -> Option[T]:
    if (value is None):
        return _some_empty_option
    return Option(value)

none = Option.empty

__all__ = \
[
    'EmptyOption',
    'Option',
    'Some',
    'none',
]
