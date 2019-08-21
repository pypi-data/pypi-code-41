"""
Author: qiacai
"""

import math
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
import time

from ada_core import exceptions, utils, constants
from ada_core.algorithms import Algorithm
from ada_core.data_model.io_data_type import AlgorithmIODataType
from ada_core.data_model.time_series import TimeSeries


class SplitByTimestamp(Algorithm):

    def __init__(self):
        super(SplitByTimestamp, self).__init__(self.__class__.__name__)

    def _run_algorithm(self, input_value, left=None, left_in_flag=None, right=None, right_in_flag=None, direct=None):

        if left_in_flag is None:
            left_in_flag = constants.ALGORITHM_DEFAULT_CALCULATOR_SPLIT_TIMESTAMP_LEFT_IN

        if right_in_flag is None:
            right_in_flag = constants.ALGORITHM_DEFAULT_CALCULATOR_SPLIT_TIMESTAMP_RIGHT_IN

        if direct is None:
            direct = constants.ALGORITHM_DEFAULT_CALCULATOR_SPLIT_TIMESTAMP_DIRECT

        output_value = input_value.splitByTimestamp(left=left, left_in_flag=left_in_flag, right=right, right_in_flag=right_in_flag,
                                            direct=direct)

        return {'output_value': output_value}


class SplitByWindow(Algorithm):
    def __init__(self):
        super(SplitByWindow, self).__init__(self.__class__.__name__)

    def _run_algorithm(self, input_value, window, timestamp=None, direct=None, left_in_flag=None, right_in_flag=None, timezone=None):

        if direct is None:
            direct = constants.ALGORITHM_DEFAULT_CALCULATOR_SPLIT_WINDOW_DIRECT

        if left_in_flag is None:
            left_in_flag = constants.ALGORITHM_DEFAULT_CALCULATOR_SPLIT_WINDOW_LEFT_IN

        if right_in_flag is None:
            right_in_flag = constants.ALGORITHM_DEFAULT_CALCULATOR_SPLIT_WINDOW_RIGHT_IN

        if timezone is None:
            timezone = constants.ALGORITHM_DEFAULT_CALCULATOR_SPLIT_WINDOW_TIMEZONE

        output_value = input_value.splitByWindow(window=window, timestamp=timestamp, direct=direct, left_in_flag=left_in_flag,
                                       right_in_flag=right_in_flag, timezone=timezone)

        return {'output_value': output_value}


class StandardNormalization(Algorithm):

    def __init__(self):
        super(StandardNormalization, self).__init__(self.__class__.__name__)
        # self.name = 'standard_normalization'

    def _run_algorithm(self, input_value):

        output_value = TimeSeries()

        mean = np.asscalar(np.average(input_value.getValueList()))
        std = np.asscalar(np.std(input_value.getValueList()))

        if std <= 0:
            for timestamp, value in input_value.items():
                output_value.update({timestamp: value})
        else:
            for timestamp, value in input_value.items():
                output_value.update({timestamp: (value - mean) / std})

        output_value = output_value

        return {'output_value': output_value}


class ScaleNormalization(Algorithm):

    def __init__(self):
        super(ScaleNormalization, self).__init__(self.__class__.__name__)
        # self.name = 'scale_normalization'

    def _run_algorithm(self, input_value):

        output_value = TimeSeries()
        max = np.asscalar(np.max(input_value.getValueList()))
        min = np.asscalar(np.min(input_value.getValueList()))

        if max <= min:
            for timestamp, value in input_value.items():
                output_value.update({timestamp: value})
        else:
            for timestamp, value in input_value.items():
                output_value.update({timestamp: (value - min) / (max - min)})

        output_value = output_value

        return {'output_value': output_value}


class ExponentialMovingAverageSmoothing(Algorithm):

    """
    return a new time series which is a EMA smoothed version of the original data series.
    soomth forward once, backward once, and then take the average.

    :param float smoothing_factor: smoothing factor
    :param str smoothing_direction: smoothing direction, including forward, backward, and both
    :return: :class:`TimeSeries` object.
    """

    def __init__(self):
        super(ExponentialMovingAverageSmoothing, self).__init__(self.__class__.__name__)
        # self.name = 'exponential_smooth'

    def _run_algorithm(self, input_value, smoothing_factor=None, smoothing_direction=None):

        if smoothing_factor is None:
            smoothing_factor = constants.ALGORITHM_DEFAULT_CALCULATOR_EXPONENTIAL_MA_SMOOTHING_FACTOR

        if smoothing_direction is None:
            smoothing_direction = constants.ALGORITHM_DEFAULT_CALCULATOR_EXPONENTIAL_MA_SMOOTHING_DIRECTION

        forward_smooth = {}
        backward_smooth = {}
        output_value = {}

        pre_entry = input_value.getValueList()[0]
        next_entry = input_value.getValueList()[-1]


        # for key, value in input_value.items():
        #     forward_smooth[key] = smoothing_factor * pre_entry + (1 - smoothing_factor) * value
        #     pre_entry = forward_smooth[key]
        #
        # for key in reversed(input_value.getKeyList()):
        #     value = input_value.get(key)
        #     backward_smooth[key] = smoothing_factor * next_entry + (1 - smoothing_factor) * value
        #     next_entry = backward_smooth[key]
        #
        # for key in forward_smooth.keys():
        #     output_value[key] = (forward_smooth[key] + backward_smooth[key]) / 2


        if smoothing_direction == 'forward':
            for key, value in input_value.items():
                forward_smooth[key] = smoothing_factor * pre_entry + (1 - smoothing_factor) * value
                pre_entry = forward_smooth[key]

            resultTs = TimeSeries(forward_smooth)

        elif smoothing_direction == 'backward':
            for key in reversed(input_value.getKeyList()):
                value = input_value.get(key)
                backward_smooth[key] = smoothing_factor * next_entry + (1 - smoothing_factor) * value
                next_entry = backward_smooth[key]

            resultTs = TimeSeries(backward_smooth)

        else:
            for key, value in input_value.items():
                forward_smooth[key] = smoothing_factor * pre_entry + (1 - smoothing_factor) * value
                pre_entry = forward_smooth[key]

            for key in reversed(input_value.getKeyList()):
                value = input_value.get(key)
                backward_smooth[key] = smoothing_factor * next_entry + (1 - smoothing_factor) * value
                next_entry = backward_smooth[key]

            for key in forward_smooth.keys():
                output_value[key] = (forward_smooth[key] + backward_smooth[key]) / 2

            resultTs = TimeSeries(output_value)

        output_value = resultTs

        return {'output_value': output_value}


class SimpleMovingAverageSmoothing(Algorithm):

    """
    return a new time series which is a SMA smoothed version of the original data series.
    soomth forward once, backward once, and then take the average if both was chosen

    :param str smoothing_window: smoothing window to select
    :param str smoothing_direction: smoothing direction, including forward, backward, and both
    :return: :class:`TimeSeries` object.
    """

    def __init__(self):
        super(SimpleMovingAverageSmoothing, self).__init__(self.__class__.__name__)

    def _run_algorithm(self, input_value, smoothing_window=None, smoothing_direction=None, timezone=None):

        if smoothing_window is None:
            smoothing_window = constants.ALGORITHM_DEFAULT_CALCULATOR_SIMPLE_MA_SMOOTHING_WINDOW

        if smoothing_direction is None:
            smoothing_direction = constants.ALGORITHM_DEFAULT_CALCULATOR_SIMPLE_MA_SMOOTHING_DIRECTION

        if timezone is None:
            timezone = constants.ALGORITHM_DEFAULT_CALCULATOR_SIMPLE_MA_TIMEZONE

        forward_smooth = {}
        backward_smooth = {}
        both_value = {}

        if smoothing_window[0] == '-':
            smoothing_window_forward = smoothing_window[1:]
            smoothing_window_backward = smoothing_window
        else:
            smoothing_window_forward = smoothing_window
            smoothing_window_backward = '-' + str(smoothing_window)

        # t0 = time.time()
        # for key, value in input_value.items():
        #     input_value_slide = input_value.splitByWindow(smoothing_window_forward, timestamp=key, left_in_flag=True, right_in_flag=False, timezone=timezone)
        #     forward_smooth[key] = input_value_slide.mean()
        # print("smoothing forward: {}".format(time.time()-t0))
        # for key in reversed(input_value.getKeyList()):
        #     input_value_slide = input_value.splitByWindow(smoothing_window_backward, timestamp=key, left_in_flag=False, right_in_flag=True, timezone=timezone)
        #     backward_smooth[key] = input_value_slide.mean()
        # print("smoothing backward: {}".format(time.time()-t0))
        # for key in forward_smooth.keys():
        #     both_value[key] = (forward_smooth[key] + backward_smooth[key]) / 2
        # print("cal_both: {}".format(time.time()-t0))

        if smoothing_direction == 'forward':
            for key, value in input_value.items():
                input_value_slide = input_value.splitByWindow(smoothing_window_forward, timestamp=key, left_in_flag=True, right_in_flag=False, timezone=timezone)
                forward_smooth[key] = input_value_slide.mean()

            resultTs = TimeSeries(forward_smooth)
        elif smoothing_direction == 'backward':
            for key in reversed(input_value.getKeyList()):
                input_value_slide = input_value.splitByWindow(smoothing_window_backward, timestamp=key, left_in_flag=False, right_in_flag=True, timezone=timezone)
                backward_smooth[key] = input_value_slide.mean()

            resultTs = TimeSeries(backward_smooth)
        else:
            for key, value in input_value.items():
                input_value_slide = input_value.splitByWindow(smoothing_window_forward, timestamp=key, left_in_flag=True, right_in_flag=False, timezone=timezone)
                forward_smooth[key] = input_value_slide.mean()
            for key in reversed(input_value.getKeyList()):
                input_value_slide = input_value.splitByWindow(smoothing_window_backward, timestamp=key, left_in_flag=False, right_in_flag=True, timezone=timezone)
                backward_smooth[key] = input_value_slide.mean()
            for key in forward_smooth.keys():
                both_value[key] = (forward_smooth[key] + backward_smooth[key]) / 2

            resultTs = TimeSeries(both_value)
        output_value = resultTs

        return {'output_value': output_value}


class SeasonalDecompose(Algorithm):

    def __init__(self):
        super(SeasonalDecompose, self).__init__(self.__class__.__name__)
        # self.name = 'seasonal_decompose'

    def _run_algorithm(self, input_value, period_window=None, trend_only=None, is_fillna=None, timezone=None):

        if period_window is None:
            period_window = constants.ALGORITHM_DEFAULT_CALCULATOR_SEASONAL_DECOMPOSE_PERIOD_WINDOW

        if trend_only is None:
            trend_only = constants.ALGORITHM_DEFAULT_CALCULATOR_SEASONAL_DECOMPOSE_TREND_ONLY

        if is_fillna is None:
            is_fillna = constants.ALGORITHM_DEFAULT_CALCULATOR_SEASONAL_DECOMPOSE_FILLNA

        if timezone is None:
            timezone = constants.ALGORITHM_DEFAULT_CALCULATOR_SEASONAL_DECOMPOSE_TIMEZONE

        # process period_window
        if str(period_window)[0]=='-':
            period_window = str(period_window)[1:]
        if period_window[0] == '0':
            raise exceptions.ParametersNotPassed('the value of period_window is invalid: {}'.format(period_window))
        try:
            # user input is number of points
            freq = int(period_window)
        except ValueError:
            # user input is timewindow
            temp_list = []
            input_value_temp = TimeSeries(input_value)

            while len(input_value_temp) > 0:
                temp_sub = input_value_temp.splitByWindow(period_window, left_in_flag=False, right_in_flag=True, timezone=timezone, direct=True)
                temp_list.append(len(temp_sub))
            if len(temp_list) <= 2:
                freq = max(temp_list)
            else:
                freq = np.argmax(np.bincount(temp_list))

        if len(input_value) <= freq:
            raise exceptions.ParametersNotPassed('ada.algorithms.transformer.seasonal_decompose: '
                                                   'the lengh of the original time series is less than one period')

        valueList = input_value.getValueList()
        valueList = [valueList.median() if math.isnan(value) else value for value in valueList]
        results = seasonal_decompose(valueList, freq=freq, two_sided=False, model='additive')

        if trend_only:
            time_series = results.trend
        else:
            time_series = results.trend + results.resid

        time_series = pd.Series(time_series, input_value.getKeyList())

        if is_fillna:
            time_series = time_series.fillna(method='bfill')
        else:
            time_series = time_series[freq:]

        output_value = TimeSeries(dict(time_series.to_dict()))

        return {'output_value': output_value}


class FilterByPeriod(Algorithm):

    def __init__(self):
        super(FilterByPeriod, self).__init__(self.__class__.__name__)

    def _run_algorithm(self, input_value, period_window=None, align_point=None, direct=None, timezone=None):

        if period_window is None:
            period_window = constants.ALGORITHM_DEFAULT_CALCULATOR_FILTER_WITH_PERIOD_PERIOD_WINDOW

        if align_point is None:
            align_point = constants.ALGORITHM_DEFAULT_CALCULATOR_FILTER_WITH_PERIOD_ALIGN_POINT

        if direct is None:
            direct = constants.ALGORITHM_DEFAULT_CALCULATOR_FILTER_WITH_PERIOD_DIRECT

        if timezone is None:
            timezone = constants.ALGORITHM_DEFAULT_CALCULATOR_FILTER_WITH_PERIOD_TIMEZONE

        output_value = input_value.filterByPeriod(period_window=period_window, align_point=align_point, direct=direct, timezone=timezone)

        return {'output_value': output_value}

