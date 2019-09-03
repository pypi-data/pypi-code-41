# -*- coding: utf-8 -*-
#! python3

"""
    This package is used to handle geographic metadata asstored as XML in ISO 19139 and 19110.
"""

# submodules
from .__about__ import __version__  # noqa: F401

# subpackages
from .models import *  # noqa: F401,F403
from .readers import *  # noqa: F401,F403
from .utils import *  # noqa: F401,F403

VERSION = __version__
