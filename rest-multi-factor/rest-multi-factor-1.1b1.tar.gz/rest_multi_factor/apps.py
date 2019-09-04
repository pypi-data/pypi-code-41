"""Standard django app config for the REST Multi Factor app."""

from django.apps import AppConfig


from rest_multi_factor.registry import registry


class RestMultiFactorConfig(AppConfig):
    """Standard Django App config for the REST Multi Factor app."""

    name = 'rest_multi_factor'

    def ready(self):
        """Initialize the registry when all models are loaded."""
        if not registry.initialized:
            registry.initialize()
