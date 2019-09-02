# -*- coding: utf-8 -*-
"""
Custom exceptions
"""

class MissingMandatoryArgument(Exception):
    """
    Raised when a mandatory argument is missing
    """
    pass


class InstanceNotFound(Exception):
    """
    Raised when no instance could be found
    """
    pass


class MultipleInstanceFound(Exception):
    """
    Raised when no instance could be found
    """
    pass
