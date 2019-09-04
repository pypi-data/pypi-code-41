"""
Serializer Registry.

Allows to map models to serializers without circular imports
or too early model imports.
"""

__all__ = (
    "registry",
    "SerializerRegistry",
)

from importlib import import_module

from django.apps import apps


class SerializerRegistry(object):
    """
    Registry for device serializers.

    This class allows to register serializers for devices that will be
    loaded if the models are initialized.
    """

    __slots__ = ("_initialized", "_serializers", "_prematurely")

    def __init__(self):
        """Initialize the class."""
        self._prematurely = {}
        self._serializers = {}
        self._initialized = False

    def __getitem__(self, device):
        """Retrieve the serializer for a device."""
        if not self.initialized:
            raise RuntimeError("The registry isn't initialized yet")

        return self._serializers[device]

    def initialize(self):
        """
        Initialize the registry.

        This method will import all the registered devices and
        serializers and put them into a mapping.
        """
        if self.initialized:
            raise RuntimeError("The registry is already initialized")

        for specifier, serializer in self._prematurely.items():
            model = apps.get_model(specifier)
            self._serializers[model] = self._get_serializer(model, serializer)

        self._initialized = True

    def register(self, specifier, serializer):
        """
        Register a device (specifier).

        The device should be registered as '<app_label>.<model_name>'
        and the serializer as '<module_name>.<serializer_name>'.

        :param specifier: The device specifier
        :type specifier: str

        :param serializer: The serializer specifier
        :type serializer: str
        """
        if self.initialized:
            raise RuntimeError("The registry is already initialized")

        if specifier in self._prematurely.keys():
            if serializer == self._prematurely[specifier]:
                raise RuntimeError("Double register for {0}".format(specifier))

            return  # pragma: no cover

        self._prematurely[specifier] = serializer

    def _get_serializer(self, model, serializer):
        """
        Get a serializer from a app and serializer specifier.

        :param model: The loaded model where the serializer lives
        :type model: model

        :param serializer: The serializer specifier
        :type serializer: str

        :return: The serializer class that was specified
        :rtype: type of rest_framework.serializers.Serializer
        """
        app_lbl = getattr(model, "_meta").app_label
        package = apps.get_app_config(app_lbl).module

        if "." in serializer:  # pragma: no cover
            module, serializer = serializer.split(".", 1)

        else:
            module = "serializers"

        module = import_module(".".join((package.__name__, module)))
        return getattr(module, serializer)

    @property
    def initialized(self):
        """
        Check if the registry is initialized.

        :return: Whether the registry is initialized or not
        :rtype: bool
        """
        return self._initialized


registry = SerializerRegistry()
