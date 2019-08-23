# coding=utf-8
from typing import Callable, Generic, TypeVar


ValueType = TypeVar('ValueType')


class LazyValue(Generic[ValueType], object):
    def __init__(self, find_value):
        # type: (Callable[[], ValueType]) -> None
        self._find_value = find_value
        self._value_found = False
        self._value = None

    @property
    def value(self):
        # type: () -> ValueType
        if not self._value_found:
            self._value = self._find_value()
            self._value_found = True

        return self._value
