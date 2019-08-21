"""
Author: qiacai
"""

import math
import numpy as np
import pandas as pd

from ada_core import exceptions, utils, constants
from ada_core.algorithms import Algorithm
from ada_core.data_model.io_data_type import AlgorithmIODataType
from ada_core.data_model.time_series import TimeSeries


class NaiveAlgorithm(Algorithm):

    def __init__(self):
        super(NaiveAlgorithm, self).__init__(self.__class__.__name__)

    def _run_algorithm(self, input_value):
        output_value = input_value
        return {'output_value': output_value}


class Round(Algorithm):
    def __init__(self):
        super(Round, self).__init__(self.__class__.__name__)

    def _run_algorithm(self, input_value, ndigits=None):

        if ndigits is None:
            ndigits = constants.ALGORITHM_DEFAULT_CALCULATOR_ROUND_NDIGITS

        output_value = round(input_value, ndigits)
        return {'output_value': output_value}


class Abs(Algorithm):
    def __init__(self):
        super(Abs, self).__init__(self.__class__.__name__)

    def _run_algorithm(self, input_value):
        output_value = abs(input_value)
        return {'output_value': output_value}


class Neg(Algorithm):
    def __init__(self):
        super(Neg, self).__init__(self.__class__.__name__)

    def _run_algorithm(self, input_value):
        output_value = -input_value
        return {'output_value': output_value}


class TimeOffset(Algorithm):

    def __init__(self):
        super(TimeOffset, self).__init__(self.__class__.__name__)

    def _run_algorithm(self, input_value, offset_window=None, timezone=None):

        if offset_window is None:
            offset_window = constants.ALGORITHM_DEFAULT_CALCULATOR_TIME_OFFSET_OFFSET_WINDOW
        if timezone is None:
            timezone = constants.ALGORITHM_DEFAULT_TIMEZONE

        output_value = input_value.timeOffset(offset_window, timezone)
        return {'output_value': output_value}