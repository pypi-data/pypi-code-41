# -*- coding: utf-8 -*-
"""Domain Driven Design framework."""
from .nginx_base_exception import NginxBaseException


class ServerError(NginxBaseException):

    """Generic exception for Nginx root"""
    def __init__(self, msg="Server error", original_exception=None):
        super(ServerError, self).__init__(msg + (": %s" % original_exception))
        self.original_exception = original_exception
