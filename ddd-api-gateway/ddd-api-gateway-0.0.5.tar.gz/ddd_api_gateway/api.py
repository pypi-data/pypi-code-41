# -*- coding: utf-8 -*-
"""Domain Driven Design framework."""
import uuid
from ddd_base import Entity
from .prototype import Prototype


class Api(Entity, Prototype):

    def __init__(self, name, path, specs):
        super().__init__()
        self.name = name
        self.path = path
        self.specs = specs

    def clone(self, **kwargs):
        api_copy = self.__class__(self.name, self.path, self.specs)
        api_copy.__dict__.update(**kwargs)
        api_copy.id = uuid.uuid1()
        return api_copy
