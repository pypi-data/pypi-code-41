"""
KomaPy chart series.
"""

from collections import Callable

from .constants import SUPPORTED_NAMES, SUPPORTED_TYPES
from .exceptions import ChartError
from .utils import get_validation_methods

addon_registers = {

}


def register_addon(name, resolver):
    """
    Register add-on function.
    """
    if not isinstance(resolver, Callable):
        raise ChartError('Add-on resolver must be callable')

    if name in addon_registers:
        raise ChartError('Add-on name already exists')

    addon_registers[name] = resolver


class Series(object):
    """A series object."""

    required_parameters = ['fields']
    available_parameters = {
        'name': None,
        'query_params': {},
        'fields': [],
        'plot_params': {},
        'labels': {},
        'locator': {},
        'formatter': {},
        'aggregations': [],
        'transforms': [],
        'secondary': None,
        'legend': {},
        'title': None,
        'type': 'line',
        'xaxis_date': False,
        'yaxis_date': False,
        'url': None,
        'csv': None,
        'csv_params': {},
        'grid': {},
        'addons': [],
    }

    def __init__(self, **kwargs):
        for key, value in self.available_parameters.items():
            if key in kwargs:
                setattr(self, key, kwargs[key])
            else:
                setattr(self, key, value)

        self._check_required_parameters(kwargs)

    def _check_required_parameters(self, kwargs):
        for param in self.required_parameters:
            if param not in kwargs:
                raise ChartError('Parameter {} is required'.format(param))

    def validate_name(self):
        """Validate name attribute."""
        if self.name:
            if self.name not in SUPPORTED_NAMES:
                raise ChartError('Unknown parameter name {}'.format(self.name))

    def validate_type(self):
        """Validate type attribute."""
        if self.type not in SUPPORTED_TYPES:
            raise ChartError('Unsupported plot type {}'.format(self.name))

    def validate_fields(self):
        """Validate fields attribute."""
        if not self.fields:
            raise ChartError('Series fields must be set')

    def validate(self):
        """Validate all config attributes."""
        validation_methods = get_validation_methods(Series)

        for method in validation_methods:
            getattr(self, method)()
