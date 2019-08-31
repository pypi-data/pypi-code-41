# -*- coding: utf-8 -*-

"""Top-level package for Python port of R's Comprehensive Dynamic Time Warp algorithm package."""

__author__ = """Toni Giorgino"""
__email__ = 'toni.giorgino@gmail.com'
__version__ = '0.4.2'


from .dtw import *
from .stepPattern import *
from .data import *
from .countPaths import *
from .dtwPlot import *
from .mvm import *
from .warp import *
from .warpArea import *
from .window import *

import __main__ as main


print("""Please don't use this package. It has been superseded by dtw-python. See https://DynamicTimeWarping.github.io \n""")


