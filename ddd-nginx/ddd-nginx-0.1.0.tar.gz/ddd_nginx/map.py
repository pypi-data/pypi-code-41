# -*- coding: utf-8 -*-
"""Domain Driven Design framework."""
from ddd_base import ValueObject
from collections import namedtuple
from .block import Block

MapDefinition = namedtuple('MapDefinition', ['key', 'value'])
MapKeyParis = namedtuple('MapKeyParis', ['key', 'value'])


class Map(ValueObject, Block):

    def __init__(self, definition=None):
        super().__init__()
        self.definition = definition
        self.key_pairs = []

    def __eq__(self, other):
        if not isinstance(other, Map):
            return NotImplemented

        return self.definition.key == self.definition.key \
            and self.definition.value == other.definition.value \
            and self.key_pairs == other.key_pairs

    def append(self, block):
        self.key_pairs.append(block)
