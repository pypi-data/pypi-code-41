"""Standard django app config for the HOTP app."""

__all__ = (
    "HOTPConfig",
)

from django.apps import AppConfig


class HOTPConfig(AppConfig):
    """Standard Django App config for the HOTP app."""

    name = "rest_multi_factor.plugins.hotp"
