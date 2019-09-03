# -*- coding: utf-8 -*-
"""Domain Driven Design framework."""


class UpstreamRepository:

    def __init__(self, upstreams=None):
        upstreams = upstreams if upstreams else []

        self.upstreams = upstreams

    def find(self, upstream_id):
        the_upstream = None
        for upstream in self.upstreams:
            if upstream.id == upstream_id:
                the_upstream = upstream
                break

        return the_upstream

    def find_by_name(self, upstream_name):
        the_upstream = None
        for upstream in self.upstreams:
            if upstream.name == upstream_name:
                the_upstream = upstream
                break

        return the_upstream

    def find_all(self):
        return self.upstreams
