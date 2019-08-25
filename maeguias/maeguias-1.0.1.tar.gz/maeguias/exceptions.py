from __future__ import unicode_literals
from click import ClickException


class MaeGuiasException(ClickException):
    """Base exceptions for all MaeGuias Exceptions"""


class ConfigurationError(MaeGuiasException):
    """Error in configuration"""
