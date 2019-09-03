# -*- coding: utf-8 -*-
"""Domain Driven Design framework."""


class ApiGWValidator(object):

    def check_metadata(self, metadata):
        raise NotImplementedError

    def check_api(self, metadata):
        raise NotImplementedError

    def check_upstream(self, metadata):
        raise NotImplementedError

    def check_route_specification(self, route_specification):
        raise NotImplementedError


class ApiGWValidatorV1(ApiGWValidator):
    def check_metadata(self, metadata):
        check_result = False
        if metadata is not None:
            if 'author' in metadata \
                    and 'email' in metadata \
                    and 'description' in metadata \
                    and 'repository' in metadata:
                check_result = True
        return check_result

    def check_api(self, api):
        check_result = False
        if api is not None:
            if 'name' in api \
                    and 'specs' in api \
                    and 'path' in api \
                    and 'description' in api:
                check_result = True
        return check_result

    def check_upstream(self, metadata):
        check_result = False
        if metadata is not None:
            if 'name' in metadata \
                    and 'endpoints' in metadata:
                check_result = True
        return check_result

    def check_route_specification(self, route_specification):
        check_result = False
        if route_specification is not None:
            if 'apiRef' in route_specification \
                and 'upstreamRef' in route_specification \
                    and 'policies' in route_specification:
                check_result = True
        return check_result


def create_api_gw_validator(version="v1"):
    """Factory"""
    api_gw_validator = {
        "v1": ApiGWValidatorV1
    }

    return api_gw_validator[version]()
