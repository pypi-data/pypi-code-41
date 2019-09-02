# coding: utf-8
#! python3  # noqa: E265

# imports
from collections import namedtuple

# Column namedtuple
ColumnPattern = namedtuple("Column", ["letter", "wrap"])

from .raster import RASTER_COLUMNS  # noqa: F401
from .resource import RESOURCE_COLUMNS  # noqa: F401
from .service import SERVICE_COLUMNS  # noqa: F401
from .vector import VECTOR_COLUMNS  # noqa: F401
