# -*- coding: utf-8 -*-
"""Domain Driven Design framework."""
from .api_gateway_base_exception import ApiGWBaseException


class ApiGWApiError(ApiGWBaseException):

    """Generic exception for ApiGW metadata"""
    def __init__(self, msg="Api format error", original_exception=None):
        super(ApiGWApiError, self).__init__(msg + (": %s" % original_exception))
        self.original_exception = original_exception
