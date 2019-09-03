# -*- coding: utf-8 -*-
"""Domain Driven Design framework."""
from ddd_base import Aggregate


class ApiGW(Aggregate):

    def __init__(self):
        super(ApiGW, self).__init__()
        self.version = None
        self.namespace = None
        self.metadata = None
        self.apis = []
        self.upstreams = []
        self.route_specifications = []
