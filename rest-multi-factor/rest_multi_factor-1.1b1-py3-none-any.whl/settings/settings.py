"""
Here is the main settings handler defined.

This class is responsible for loading custom settings.
"""

__all__ = (
    "MultiFactorSettings",
)

from django.conf import settings
from django.test.signals import setting_changed


from rest_framework.settings import APISettings


class MultiFactorSettings(APISettings):
    """
    Main settings handler.

    This class is responsible for loading and updating custom settings.
    """

    def __init__(self, user_settings=None, defaults=None,
                 import_strings=None, namespace=None):
        """
        Initialize the settings.

        :param user_settings: The pre-set user settings.
        :type user_settings: dict | None

        :param defaults: The default settings to use
        :type defaults: dict | None

        :param import_strings: The names of the importable settings
        :type import_strings: iterable of str | None

        :param namespace: The namespace of the settings or "CUSTOM"
        :type namespace: str | None
        """
        APISettings.__init__(self, user_settings, defaults, import_strings)

        self.namespace = namespace or "CUSTOM"
        setting_changed.connect(self.reload_settings)

    @property
    def user_settings(self):
        """
        Retrieve the user settings.

        These are the settings that are defined in the main settings
        file.

        :return: The user defined settings
        :rtype dict
        """
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, self.namespace, {})
        return self._user_settings

    def reload_settings(self, *_, setting=None, **__):  # pragma: no cover
        """
        Reload the settings when the settings file has changed.

        :param setting: The name of the setting that has been changed
        :type setting: str
        """
        if setting == self.namespace:
            self.reload()

    def register(self, defaults, import_strings=None):
        """
        Register a additional set of configurations that are available.

        This method can be used by plugins to keep configurations within
        the same namespace.

        :param defaults: The additional defaults that are added.
        :type defaults: dict

        :param import_strings: The names of the settings that need to be loaded
        :type import_strings: list of str
        """
        import_strings = import_strings or []

        duplicates = set(self.defaults.keys()) & set(defaults.keys())
        if len(duplicates) != 0:  # pragma: no cover
            raise RuntimeError(
                "Duplicate settings found: {0}".format(', '.join(duplicates))
            )

        not_existing = set(import_strings) - set(defaults.keys())
        if len(not_existing) != 0:  # pragma: no cover
            raise RuntimeError(
                "Non-existing import strings found: {0}".format(
                    ', '.join(not_existing)
                )
            )

        self.defaults.update(defaults)
        self.import_strings += import_strings
