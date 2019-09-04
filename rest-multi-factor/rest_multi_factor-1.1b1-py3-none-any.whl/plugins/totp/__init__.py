"""
TOTP plugin for the rest multi factor package.

TOTP can also be integrated with Google authenticator.
"""

from rest_multi_factor.registry import registry
from rest_multi_factor.settings import multi_factor_settings
from rest_multi_factor.plugins.totp.settings import DEFAULTS, LOADABLE


duplicates = set(multi_factor_settings.defaults.keys()) & set(DEFAULTS.keys())
if not bool(len(duplicates)):
    multi_factor_settings.register(DEFAULTS, LOADABLE)

if not registry.initialized:
    registry.register("totp.TOTPDevice", "TOTPDeviceSerializer")

default_app_config = "rest_multi_factor.plugins.totp.apps.TOTPConfig"
