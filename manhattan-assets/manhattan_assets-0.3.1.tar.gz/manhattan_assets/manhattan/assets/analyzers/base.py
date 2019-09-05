"""
Classes for describing asset analyzers to storage backends.
"""

import copy

__all__ = [
    'BaseAnalyzer',
    'CustomAnalyzer'
]


class AnalyzerMeta(type):
    """
    Meta class for analyzersa which adds the analyzer class to the register of
    analyzers.
    """

    def __new__(meta, name, bases, dct):

        cls = super().__new__(meta, name, bases, dct)

        if name != 'BaseAnalyzer' \
                and bases \
                and not cls._exclude_from_register:

            # Register the analyzer
            BaseAnalyzer._analyzers[cls._id] = cls

        return cls


class BaseAnalyzer(metaclass=AnalyzerMeta):
    """
    Analyzer classes provide a mechanism for describe how to analyze an
    asset, for example finding the dominent colours in an image, or the number
    of frames of animation, etc.

    Each backend asset manager is responsible for translating an analyzer
    instance into the necessary instuctions for the storage service it
    represents.

    An analyzer is made up of a unique Id and the settings that will be used
    when applying it. Settings should be set as a dictionary and values should
    be JSON safe.

    An analyzer's Id is typically set as a static class property, and should
    use the following format:

        `{asset_type}.{analyzer}` -> `image.animation`

    backend (service) specific analyzers should be postfixed, e.g:

        `{backend}.{asset_type}.{analyzer}` -> `hangar51.image.dominant_colors`

    All backends should support non-specific analyzers.
    """

    # The analyzer's unique Id
    _id = ''

    # A table of all registered analyzers (e.g `{id: analyzer_class}`)
    _analyzers = {}

    # Flag indicating if the analyzer should be excluded from the register of
    # analyzers.
    _exclude_from_register = False

    def __init__(self, settings=None):

        # The settings that will be used when applying the analyzer
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
        Return a dictionary for the analyzer with values converted to JSON
        safe types.
        """
        return {'id': self.id, 'settings': self.settings}

    @classmethod
    def from_json_type(cls, json_type_data):
        """Convert a JSON safe dictionary of to an analyzer instance"""

        analyzer_cls = cls._analyzers.get(json_type_data['id'])

        if analyzer_cls:
            return analyzer_cls(**json_type_data['settings'])

        return CustomAnalyzer(
            json_type_data['id'],
            json_type_data['settings']
        )


class CustomAnalyzer(BaseAnalyzer):
    """
    A custom analyzer, typically returned by the `from_json_type` class method
    when their is no matching analyzer registered (useful for ad hoc,
    backend / service specific analyzers).
    """

    _exclude_from_register = True

    def __init__(self, id, **settings):

        # The Id for the custom analyzer
        self._id = id

        # The settings that will be used when applying the analyzer
        self._settings = settings
