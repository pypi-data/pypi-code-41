# -*- coding: utf-8 -*-
#! python3

"""
    This package is used to export Isogeo metadata into Excel workbooks using the Isogeo Python SDK and OpenPyXl.
"""

# submodules
from .__about__ import __version__  # noqa: F401
from .isogeo2xlsx import Isogeo2xlsx  # noqa: F401

# subpackages
from .matrix import *  # noqa: F401,F403
from .utils import *  # noqa: F401,F403

VERSION = __version__
