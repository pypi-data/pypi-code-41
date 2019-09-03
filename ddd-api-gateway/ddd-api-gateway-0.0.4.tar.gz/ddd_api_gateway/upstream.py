# -*- coding: utf-8 -*-
"""Domain Driven Design framework."""
import uuid
from ddd_base import Entity
from .prototype import Prototype


class Upstream(Entity, Prototype):

    def __init__(self, name, endpoints):
        super(Upstream, self).__init__()
        self.name = name
        self.endpoints = endpoints

    def clone(self, **kwargs):
        upstream_copy = self.__class__(self.name, self.endpoints)
        upstream_copy.__dict__.update(**kwargs)
        upstream_copy.id = uuid.uuid1()
        return upstream_copy
