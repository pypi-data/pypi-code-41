#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: asr
"""

from typing import NewType, Tuple, Any
import numpy as np
import scipy.optimize as opt
import matplotlib
from matplotlib.axes._subplots import Axes

# Defining the Matrix type (numpy.ndarray)
Matrix = NewType('Matrix', np.ndarray)
# defining matplotlib.axes
Axes = NewType('AxesSubplot', Axes)
# defining a basic tuple
Pair = Tuple[float, float]
# Optimization results (scipy)
OptimizeResult = NewType('OptimizeResult', opt.optimize.OptimizeResult)
