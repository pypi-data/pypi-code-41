"""
Author: qiacai
"""
from numbers import Number
import numpy as np

from ada_core import exceptions, utils, constants
from ada_core.algorithms import Algorithm
from ada_core.data_model.io_data_type import AlgorithmIODataType
from ada_core.data_model.time_series import TimeSeries
from ada_core.data_model.entry import Entry


class ValueArithmetic(Algorithm):

    def __init__(self):
        super(ValueArithmetic, self).__init__(self.__class__.__name__)

    def _run_algorithm(self, input_value, operator, fill_value=None):

        if fill_value is None:
            fill_value = constants.ALGORITHM_DEFAULT_CALCULATOR_VALUE_ARITHMETIC_FILL_VALUE

        if operator == "*":
            if isinstance(input_value.left, TimeSeries) or isinstance(input_value.left, Entry):
                if isinstance(input_value.left, TimeSeries):
                    output_value = input_value.left.mul(input_value.right, fill_value)
                else:
                    output_value = input_value.left.mul(input_value.right)
            elif isinstance(input_value.right, TimeSeries) or isinstance(input_value.right, Entry):
                if isinstance(input_value.right, TimeSeries):
                    output_value = input_value.right.rmul(input_value.left, fill_value)
                else:
                    output_value = input_value.right.rmul(input_value.left)
            else:
                output_value = input_value.left * input_value.right

        elif operator == '/':
            if isinstance(input_value.left, TimeSeries) or isinstance(input_value.left, Entry):
                if isinstance(input_value.left, TimeSeries):
                    output_value = input_value.left.truediv(input_value.right, fill_value)
                else:
                    output_value = input_value.left.truediv(input_value.right)
            elif isinstance(input_value.right, TimeSeries) or isinstance(input_value.right, Entry):
                if isinstance(input_value.right, TimeSeries):
                    output_value = input_value.right.rtruediv(input_value.left, fill_value)
                else:
                    output_value = input_value.right.rtruediv(input_value.left)
            else:
                output_value = input_value.left / input_value.right

        elif operator == '+':
            if isinstance(input_value.left, TimeSeries) or isinstance(input_value.left, Entry):
                if isinstance(input_value.left, TimeSeries):
                    output_value = input_value.left.add(input_value.right, fill_value)
                else:
                    output_value = input_value.left.add(input_value.right)
            elif isinstance(input_value.right, TimeSeries) or isinstance(input_value.right, Entry):
                if isinstance(input_value.right, TimeSeries):
                    output_value = input_value.right.radd(input_value.left, fill_value)
                else:
                    output_value = input_value.right.radd(input_value.left)
            else:
                output_value = input_value.left + input_value.right

        elif operator == '-':
            if isinstance(input_value.left, TimeSeries) or isinstance(input_value.left, Entry):
                if isinstance(input_value.left, TimeSeries):
                    output_value = input_value.left.sub(input_value.right, fill_value)
                else:
                    output_value = input_value.left.sub(input_value.right)
            elif isinstance(input_value.right, TimeSeries) or isinstance(input_value.right, Entry):
                if isinstance(input_value.right, TimeSeries):
                    output_value = input_value.right.rsub(input_value.left, fill_value)
                else:
                    output_value = input_value.right.rsub(input_value.left)
            else:
                output_value = input_value.left - input_value.right

        elif operator == '//':
            if isinstance(input_value.left, TimeSeries) or isinstance(input_value.left, Entry):
                if isinstance(input_value.left, TimeSeries):
                    output_value = input_value.left.floordiv(input_value.right, fill_value)
                else:
                    output_value = input_value.left.floordiv(input_value.right)
            elif isinstance(input_value.right, TimeSeries) or isinstance(input_value.right, Entry):
                if isinstance(input_value.right, TimeSeries):
                    output_value = input_value.right.rfloordiv(input_value.left, fill_value)
                else:
                    output_value = input_value.right.rfloordiv(input_value.left)
            else:
                output_value = input_value.left // input_value.right

        elif operator == '%':
            if isinstance(input_value.left, TimeSeries) or isinstance(input_value.left, Entry):
                if isinstance(input_value.left, TimeSeries):
                    output_value = input_value.left.mod(input_value.right, fill_value)
                else:
                    output_value = input_value.left.mod(input_value.right)
            elif isinstance(input_value.right, TimeSeries) or isinstance(input_value.right, Entry):
                if isinstance(input_value.right, TimeSeries):
                    output_value = input_value.right.rmod(input_value.left, fill_value)
                else:
                    output_value = input_value.right.rmod(input_value.left)
            else:
                output_value = input_value.left % input_value.right

        elif operator == '**':
            if isinstance(input_value.left, TimeSeries) or isinstance(input_value.left, Entry):
                if isinstance(input_value.left, TimeSeries):
                    output_value = input_value.left.pow(input_value.right, fill_value)
                else:
                    output_value = input_value.left.pow(input_value.right)
            elif isinstance(input_value.right, TimeSeries) or isinstance(input_value.right, Entry):
                raise ValueError("The power operator value should only be numeric")
            else:
                output_value = input_value.left ** input_value.right
        else:
            raise exceptions.ParametersNotPassed("The input operator should be in ['*', '/', '+', '-', '//', '%', '**']")

        return {"output_value": output_value}


class ValueComparison(Algorithm):

    def __init__(self):
        super(ValueComparison, self).__init__(self.__class__.__name__)

    def _run_algorithm(self, input_value, operator, fill_value=None):

        if fill_value is None:
            fill_value = constants.ALGORITHM_DEFAULT_CALCULATOR_VALUE_COMPARISON_FILL_VALUE

        if operator == ">":
            if isinstance(input_value.left, TimeSeries) or isinstance(input_value.left, Entry):
                if isinstance(input_value.left, TimeSeries):
                    output_value = input_value.left.gt(input_value.right, fill_value)
                else:
                    output_value = input_value.left.gt(input_value.right)
            elif isinstance(input_value.right, TimeSeries) or isinstance(input_value.right, Entry):
                if isinstance(input_value.right, TimeSeries):
                    output_value = input_value.right.lt(input_value.left, fill_value)
                else:
                    output_value = input_value.right.lt(input_value.left)
            else:
                output_value = input_value.left > input_value.right

        elif operator == ">=":
            if isinstance(input_value.left, TimeSeries) or isinstance(input_value.left, Entry):
                if isinstance(input_value.left, TimeSeries):
                    output_value = input_value.left.ge(input_value.right, fill_value)
                else:
                    output_value = input_value.left.ge(input_value.right)
            elif isinstance(input_value.right, TimeSeries) or isinstance(input_value.right, Entry):
                if isinstance(input_value.right, TimeSeries):
                    output_value = input_value.right.le(input_value.left, fill_value)
                else:
                    output_value = input_value.right.le(input_value.left)
            else:
                output_value = input_value.left >= input_value.right

        elif operator == "<":
            if isinstance(input_value.left, TimeSeries) or isinstance(input_value.left, Entry):
                if isinstance(input_value.left, TimeSeries):
                    output_value = input_value.left.lt(input_value.right, fill_value)
                else:
                    output_value = input_value.left.lt(input_value.right)
            elif isinstance(input_value.right, TimeSeries) or isinstance(input_value.right, Entry):
                if isinstance(input_value.right, TimeSeries):
                    output_value = input_value.right.gt(input_value.left, fill_value)
                else:
                    output_value = input_value.right.gt(input_value.left)
            else:
                output_value = input_value.left < input_value.right

        elif operator == "<=":
            if isinstance(input_value.left, TimeSeries) or isinstance(input_value.left, Entry):
                if isinstance(input_value.left, TimeSeries):
                    output_value = input_value.left.le(input_value.right, fill_value)
                else:
                    output_value = input_value.left.le(input_value.right)
            elif isinstance(input_value.right, TimeSeries) or isinstance(input_value.right, Entry):
                if isinstance(input_value.right, TimeSeries):
                    output_value = input_value.right.ge(input_value.left, fill_value)
                else:
                    output_value = input_value.right.ge(input_value.left)
            else:
                output_value = input_value.left <= input_value.right

        elif operator == "==":
            if isinstance(input_value.left, TimeSeries) or isinstance(input_value.left, Entry):
                if isinstance(input_value.left, TimeSeries):
                    output_value = input_value.left.eq(input_value.right, fill_value)
                else:
                    output_value = input_value.left.eq(input_value.right)
            elif isinstance(input_value.right, TimeSeries) or isinstance(input_value.right, Entry):
                if isinstance(input_value.right, TimeSeries):
                    output_value = input_value.right.eq(input_value.left, fill_value)
                else:
                    output_value = input_value.right.eq(input_value.left)
            else:
                output_value = input_value.left == input_value.right

        else:
            raise exceptions.ParametersNotPassed("The input operator should be in ['>', '>=', '<', '<=', '==']")

        return {'output_value': output_value}


class ValueFilter(Algorithm):

    def __init__(self):
        super(ValueFilter, self).__init__(self.__class__.__name__)

    def _run_algorithm(self, input_value, operator):

        def filter_mask_ts(input_value):
            after_filter = TimeSeries()
            for timestamp, value in input_value.items():
                if value <= 0:
                    continue
                else:
                    after_filter.update({timestamp, value})
            return after_filter

        if operator == ">":
            if isinstance(input_value.left, TimeSeries) or isinstance(input_value.left, Entry):
                mask = input_value.left.gt(input_value.right)
            elif isinstance(input_value.right, TimeSeries) or isinstance(input_value.right, Entry):
                mask = input_value.right.lt(input_value.left)
            else:
                mask = input_value.left > input_value.right

        elif operator == ">=":
            if isinstance(input_value.left, TimeSeries) or isinstance(input_value.left, Entry):
                mask = input_value.left.ge(input_value.right)
            elif isinstance(input_value.right, TimeSeries) or isinstance(input_value.right, Entry):
                mask = input_value.right.le(input_value.left)
            else:
                mask = input_value.left >= input_value.right

        elif operator == "<":
            if isinstance(input_value.left, TimeSeries) or isinstance(input_value.left, Entry):
                mask = input_value.left.lt(input_value.right)
            elif isinstance(input_value.right, TimeSeries) or isinstance(input_value.right, Entry):
                mask = input_value.right.gt(input_value.left)
            else:
                mask = input_value.left < input_value.right

        elif operator == "<=":
            if isinstance(input_value.left, TimeSeries) or isinstance(input_value.left, Entry):
                mask = input_value.left.le(input_value.right)
            elif isinstance(input_value.right, TimeSeries) or isinstance(input_value.right, Entry):
                mask = input_value.right.ge(input_value.left)
            else:
                mask = input_value.left <= input_value.right

        elif operator == "==":
            if isinstance(input_value.left, TimeSeries) or isinstance(input_value.left, Entry):
                    mask = input_value.left.eq(input_value.right)
            elif isinstance(input_value.right, TimeSeries) or isinstance(input_value.right, Entry):
                    mask = input_value.right.eq(input_value.left)
            else:
                mask = input_value.left == input_value.right

        elif operator == 'mask':
            if not isinstance(input_value.right, type(input_value.right)):
                try:
                    float(input_value.right)
                except ValueError as e:
                    raise ValueError('the mask could only be same type with left side or numeric: {}'.format(e))
            mask = input_value.right

        else:
            raise exceptions.ParametersNotPassed("The input operator should be in ['>', '>=', '<', '<=', '==']")

        if isinstance(mask, TimeSeries):
            output_value = filter_mask_ts(mask) * input_value.left
        else:
            output_value = input_value.left if mask > 0 else type(input_value.left)()

        return {'output_value': output_value}