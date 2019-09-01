# Copyright (c) 2019, Anders Lervik.
# Distributed under the MIT License. See LICENSE for more info.
"""normetapi - A package for interacting with the MET Norway Weather API."""
from .version import VERSION as __version__
from .api import location_forecast, weathericon
