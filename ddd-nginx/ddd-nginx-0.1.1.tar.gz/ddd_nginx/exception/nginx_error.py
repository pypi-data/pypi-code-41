# -*- coding: utf-8 -*-
"""Domain Driven Design framework."""
from .nginx_base_exception import NginxBaseException


class NginxError(NginxBaseException):

    """Generic exception for Nginx root"""
    def __init__(self, msg="Nginx root error", original_exception=None):
        super(NginxError, self).__init__(msg + (": %s" % original_exception))
        self.original_exception = original_exception
