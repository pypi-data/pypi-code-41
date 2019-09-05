"""
Classes for describing asset transforms to storage backends.
"""

import copy

__all__ = [
    'BaseTransform',
    'CustomTransform'
]


class TransformMeta(type):
    """
    Meta class for transforms which adds the transform class to the register
    of transforms.
    """

    def __new__(meta, name, bases, dct):

        cls = super().__new__(meta, name, bases, dct)

        if name != 'BaseTransform' \
                and bases \
                and not cls._exclude_from_register:

            # Register the transform
            BaseTransform._transforms[cls._id] = cls

        return cls


class BaseTransform(metaclass=TransformMeta):
    """
    Transform classes provide a mechanism for describe how to transform an
    asset, for example rotating and cropping an image, converting it to a
    webp, etc.

    Each backend asset manager is responsible for translating a transform
    instance into the necessary instuctions for the storage service it
    represents.

    An transform is made up of a unique Id and the settings that will be used
    when applying it. Settings should be set as a dictionary and values should
    be JSON safe.

    An transform's Id is typically set as a static class property, and should
    use the following format:

        `{asset_type}.{transform}` -> `image.crop`

    backend (service) specific transforms should be postfixed, e.g:

        `{backend}.{asset_type}.{transform}` -> `hangar51.image.single_frame`

    All backends should support non-specific transforms.
    """

    # The transform's unique Id
    _id = ''

    # A table of all registered transforms (e.g `{id: transform_class}`)
    _transforms = {}

    # Flag indicating if the transform should be excluded from the register of
    # trasforms.
    _exclude_from_register = False

    def __init__(self, settings=None):

        # The settings that will be used when applying the transform
        if settings is None:
            settings = {}

        self._settings = settings

    @property
    def id(self):
        return self._id

    @property
    def settings(self):
        return copy.deepcopy(self._settings)

    def to_json_type(self):
        """
        Return a dictionary for the transform with values converted to JSON
        safe types.
        """
        return {'id': self.id, 'settings': self.settings}

    @classmethod
    def from_json_type(cls, json_type_data):
        """Convert a JSON safe dictionary of to an transform instance"""

        transform_cls = cls._transforms.get(json_type_data['id'])

        if transform_cls:
            return transform_cls(**json_type_data['settings'])

        return CustomTransform(
            json_type_data['id'],
            **json_type_data['settings']
        )


class CustomTransform(BaseTransform):
    """
    A custom transform, typically returned by the `from_json_type` class
    method when their is no matching transform registered (useful for ad hoc,
    backend / service specific transforms).
    """

    _exclude_from_register = True

    def __init__(self, id, **settings):

        # The Id for the custom transform
        self._id = id

        # The settings that will be used when applying the transform
        self._settings = settings
