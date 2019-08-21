"""
Author: qiacai
"""
from numbers import Number
import numpy as np

from ada_core import exceptions, utils, constants
from ada_core.algorithms import Algorithm
from ada_core.data_model.io_data_type import AlgorithmIODataType
from ada_core.data_model.time_series import TimeSeries


class BaseBinaryNum1Ts2TsCalAlgorithm(Algorithm):

    def __init__(self, class_name):
        """
        Initializer

        :return:
        """

        super(BaseBinaryNum1Ts2TsCalAlgorithm, self).__init__(class_name=class_name)
        # self.name = 'base_binary_ts1num2ts_calculate'
        # self.input_type = AlgorithmIODataType.BINARY_TS_NUMBER_INPUT.value
        # self.output_type = AlgorithmIODataType.TIME_SERIES.value

    def _run_algorithm(self, **kwargs):
        raise NotImplementedError


class ValueScale(BaseBinaryNum1Ts2TsCalAlgorithm):

    def __init__(self):
        super(ValueScale, self).__init__(self.__class__.__name__)
        # self.name = 'value_scale'

    def _run_algorithm(self, input_value, operator=None):

        if operator is None:
            operator = constants.ALGORITHM_DEFAULT_CALCULATOR_VALUE_SCALE_OPERATOR

        output_value = TimeSeries()
        if operator == "*":
            for timestamp, value in input_value.right.items():
                output_value.update({timestamp: (value * input_value.left)})
        elif operator == "/":
            for timestamp, value in input_value.right.items():
                output_value.update({timestamp: (value / input_value.left)})
        elif operator == "+":
            for timestamp, value in input_value.right.items():
                output_value.update({timestamp: (value + input_value.left)})
        elif operator == "-":
            for timestamp, value in input_value.right.items():
                output_value.update({timestamp: (value - input_value.left)})
        else:
            raise exceptions.ParametersNotPassed("The input operator should be in ['*', '/', '+', '-']")

        return output_value