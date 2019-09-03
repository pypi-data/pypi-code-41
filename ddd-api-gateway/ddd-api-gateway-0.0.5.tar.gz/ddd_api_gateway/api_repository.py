# -*- coding: utf-8 -*-
"""Domain Driven Design framework."""


class ApiRepository:

    def __init__(self, apis=None):
        apis = apis if apis else []

        self.apis = apis

    def find(self, api_id):
        the_api = None
        for api in self.apis:
            if api.id == api_id:
                the_api = api
                break

        return the_api

    def find_by_name(self, api_name):
        the_api = None
        for api in self.apis:
            if api.name == api_name:
                the_api = api
                break

        return the_api

    def find_all(self):
        return self.apis
