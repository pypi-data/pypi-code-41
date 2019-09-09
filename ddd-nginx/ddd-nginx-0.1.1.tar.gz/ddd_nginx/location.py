# -*- coding: utf-8 -*-
"""Domain Driven Design framework."""
from collections import namedtuple
from ddd_base import ValueObject
from .block import Block

ReverseProxyStrategy = namedtuple('ReverseProxyStrategy', ['strategy', 'rule'])


class Location(ValueObject, Block):

    def __init__(self, name=None, scope=None, proxy=None):
        super().__init__()
        self.name = name
        self.scope = scope
        self.proxy = proxy

    def __eq__(self, other):
        if not isinstance(other, Location):
            return NotImplemented

        return self.scope == other.scope \
            and self.proxy == other.proxy \
            and self.name == other.name

    def append(self, block):
        pass
