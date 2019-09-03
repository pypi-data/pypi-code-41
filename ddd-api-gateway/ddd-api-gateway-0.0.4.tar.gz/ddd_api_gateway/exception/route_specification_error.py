# -*- coding: utf-8 -*-
"""Domain Driven Design framework."""
from .api_gateway_base_exception import ApiGWBaseException


class ApiGWRouteSpecificationError(ApiGWBaseException):

    """Generic exception for ApiGW metadata"""
    def __init__(self, msg="Route Specification format error", original_exception=None):
        super(ApiGWRouteSpecificationError, self).__init__(msg + (": %s" % original_exception))
        self.original_exception = original_exception
