# -*- coding: utf-8 -*-
"""Domain Driven Design framework."""
from ddd_base import Entity
from .block import Block
from .location import Location
from .exception.server_error import ServerError


class Server(Entity, Block):

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.locations = []

    def append(self, block):
        if isinstance(block, Location):
            self.locations.append(block)
        else:
            raise ServerError()
