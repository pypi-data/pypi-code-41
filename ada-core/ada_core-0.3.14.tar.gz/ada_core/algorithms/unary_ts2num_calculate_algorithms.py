"""
Author: qiacai
"""

import numpy as np

from ada_core import exceptions, utils, constants
from ada_core.algorithms import Algorithm
from ada_core.data_model.io_data_type import AlgorithmIODataType


class Mean(Algorithm):

    def __init__(self):
        super(Mean, self).__init__(self.__class__.__name__)

    def _run_algorithm(self, input_value, default=None):
        output_value = input_value.mean(default)
        return {'output_value': output_value}


class Median(Algorithm):

    def __init__(self):
        super(Median, self).__init__(self.__class__.__name__)

    def _run_algorithm(self, input_value, default=None):
        output_value = input_value.median(default)
        return {'output_value': output_value}


class Max(Algorithm):

    def __init__(self):
        super(Max, self).__init__(self.__class__.__name__)
        # self.name = 'max'

    def _run_algorithm(self, input_value, default=None):
        output_value = input_value.max(default)
        return {'output_value': output_value}


class Min(Algorithm):

    def __init__(self):
        super(Min, self).__init__(self.__class__.__name__)
        # self.name = 'min'

    def _run_algorithm(self, input_value, default=None):
        output_value = input_value.min(default)
        return {'output_value': output_value}


class Std(Algorithm):

    def __init__(self):
        super(Std, self).__init__(self.__class__.__name__)

    def _run_algorithm(self, input_value, default=None):
        output_value = input_value.std(default)
        return {'output_value': output_value}


class Mad(Algorithm):

    def __init__(self):
        super(Mad, self).__init__(self.__class__.__name__)
        # self.name = 'mad'

    def _run_algorithm(self, input_value, default=None):
        output_value = input_value.mad(default)
        return {'output_value': output_value}


class Count(Algorithm):

    def __init__(self):
        super(Count, self).__init__(self.__class__.__name__)

    def _run_algorithm(self, input_value, default=None):
        output_value = input_value.count(default)
        return {'output_value': output_value}


class Sum(Algorithm):

    def __init__(self):
        super(Sum, self).__init__(self.__class__.__name__)

    def _run_algorithm(self, input_value, default=None):
        output_value = input_value.sum(default)
        return {'output_value': output_value}


class Percentile(Algorithm):

    def __init__(self):
        super(Percentile, self).__init__(self.__class__.__name__)

    def _run_algorithm(self, input_value, default=None, percent=None):

        if percent is None:
            percent = constants.ALGORITHM_DEFAULT_CALCULATOR_PERCENTILE_PERCENTILE

        output_value = np.asscalar(
            np.percentile(input_value.getValueList(), percent)) if input_value.getValueList() else default

        return {'output_value': output_value}


class Cushion(Algorithm):

    def __init__(self):
        super(Cushion, self).__init__(self.__class__.__name__)

    def _run_algorithm(self, input_value, default=None, upper_percentile=None, lower_percentile=None, is_upper=None):

        if upper_percentile is None and lower_percentile is None:
            upper_percentile = constants.ALGORITHM_DEFAULT_CALCULATOR_CUSHION_UPPER_PERCENTILE
            lower_percentile = constants.ALGORITHM_DEFAULT_CALCULATOR_CUSHION_LOWER_PERCENTILE
        elif lower_percentile is None:
            lower_percentile = 100 - upper_percentile
        elif upper_percentile is None:
            upper_percentile = 100 - lower_percentile

        if is_upper is None:
            is_upper = constants.ALGORITHM_DEFAULT_CALCULATOR_CUSHION_IS_UPPER

        if input_value.getValueList():
            valueList = input_value.getValueList()
            median_value = np.asscalar(np.median(valueList))
            upper_value = np.asscalar(np.percentile(valueList, upper_percentile))
            lower_value = np.asscalar(np.percentile(valueList, lower_percentile))

            if upper_value == lower_value:
                output_value = 0.5
            else:
                if not is_upper:
                    output_value = (median_value - lower_value) / (upper_value - lower_value)
                else:
                    output_value = (upper_value - median_value) / (upper_value - lower_value)
        else:
            output_value = default

        return {'output_value': output_value}