# Copyright (c) 2018 Tulir Asokan
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from typing import Optional, Type, Generic, TypeVar


T = TypeVar('T')


class SimpleTemplate(Generic[T]):
    _template: str
    _keyword: str
    _prefix: str
    _suffix: str
    _type: Type[T]

    def __init__(self, template: str, keyword: str, prefix: str = "", suffix: str = "",
                 type: Type[T] = str) -> None:
        self._template = template
        self._keyword = keyword
        index = self._template.find("{%s}" % keyword)
        length = len(keyword) + 2
        self._prefix = prefix + self._template[:index]
        self._suffix = self._template[index + length:] + suffix
        self._type = type

    def format(self, arg: T) -> str:
        return self._template.format(**{self._keyword: arg})

    def format_full(self, arg: T) -> str:
        return f"{self._prefix}{arg}{self._suffix}"

    def parse(self, val: str) -> Optional[T]:
        if val[:len(self._prefix)] == self._prefix and val[-len(self._suffix):] == self._suffix:
            return self._type(val[len(self._prefix):-len(self._suffix)])
        return None
