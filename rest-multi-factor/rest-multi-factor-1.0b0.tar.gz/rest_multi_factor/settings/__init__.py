"""
Main settings module.

This module is responsible for loading and categorising
custom settings for multi-factor authentication.
"""


__all__ = (
    "multi_factor_settings",
)


from rest_multi_factor.settings.settings import MultiFactorSettings
from rest_multi_factor.settings.constants import NAMESPACE, DEFAULTS, LOADABLE


multi_factor_settings = MultiFactorSettings(
    None, DEFAULTS, LOADABLE, NAMESPACE
)
