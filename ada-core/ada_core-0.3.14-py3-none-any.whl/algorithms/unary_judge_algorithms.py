"""
Author: qiacai
"""

from ada_core import exceptions, constants, utils
from ada_core.algorithms import Algorithm
from ada_core.data_model.io_data_type import AlgorithmIODataType
from ada_core.data_model.time_series import TimeSeries
import time


class RefereeAlgorithm(Algorithm):

    def __init__(self, class_name):
        super(RefereeAlgorithm, self).__init__(class_name)

    def _calculate_compare_value(self, *args, **kwargs):
        raise NotImplementedError

    def get_compare_value(self, *args, **kwargs):
        return self._calculate_compare_value(*args, **kwargs)[0]

    def _calculate_bound(self, *args, **kwargs):
        raise NotImplementedError

    def get_bound(self, *args, **kwargs):
        return self._calculate_bound(*args, **kwargs)

    def _compare(self, compare_value, bound_value, operator):

        from ada_core.handler import Handler

        try:
            op_input_type = AlgorithmIODataType.BINARY_NUM_INPUT.value()
            op_input = op_input_type.to_native({'left': compare_value, 'right': bound_value})
            op_handler = Handler(algorithm_name=operator, handler_input=op_input)
            return op_handler.get_result()
        except (ValueError, AttributeError, Exception) as e:
            raise exceptions.AlgorithmCalculationError("Error when doing operator value: {}".format(e))

    # def compare(self, *args, **kwargs):
    #
    #     return self._compare(*args, **kwargs)

    def predict(self, *args, **kwargs):

        return self._compare(*args, **kwargs)


class BiRefereeAlgorithm(RefereeAlgorithm):

    def __init__(self, class_name):
        super(BiRefereeAlgorithm, self).__init__(class_name)

    def _calculate_upper_bound(self, *args, **kwargs):
        raise NotImplementedError

    def get_upper_bound(self, *args, **kwargs):
        return self._calculate_upper_bound(*args, **kwargs)

    def _calculate_lower_bound(self, *args, **kwargs):
        raise NotImplementedError

    def get_lower_bound(self, *args, **kwargs):
        return self._calculate_lower_bound(*args, **kwargs)

    def _calculate_bound(self, *args, **kwargs):
        return [self._calculate_lower_bound(*args, **kwargs), self._calculate_upper_bound(*args, **kwargs)]

    def _compare_both(self, compare_value, upper_bound_value, lower_bound_value, enclose):

        if enclose is True:
            upper_operator = '>='
            lower_operator = '<='
        else:
            upper_operator = '>'
            lower_operator = '<'

        upper_decision = self._compare(compare_value, upper_bound_value, upper_operator)
        lower_decision = self._compare(compare_value, lower_bound_value, lower_operator)

        return upper_decision or lower_decision

    # def compare(self, *args, **kwargs):
    #
    #     return self._compare_both(*args, **kwargs)

    def predict(self, *args, **kwargs):

        return self._compare_both(*args, **kwargs)


class NOTLogic(RefereeAlgorithm):
    def __init__(self):
        super(NOTLogic, self).__init__(self.__class__.__name__)

    def _calculate_compare_value(self, input_value):
        return input_value, input_value

    def _calculate_bound(self, input_value):
        return False if input_value else True

    def _compare(self, compare_value, bound_value=None, operator=None):
        return bound_value

    def _run_algorithm(self, input_value):
        compare_value = self._calculate_compare_value(input_value=input_value)
        bound_value = self._calculate_bound(input_value=input_value)
        refree_value = self._compare(compare_value=compare_value, bound_value=bound_value)
        result = {
            "output_value": refree_value,
            "extend_info": {
                "compare_value": compare_value,
                "bound_value": [bound_value]
            }
        }

        return result
        # return self._compare(compare_value=compare_value, bound_value=bound_value)


class HardThreshold(RefereeAlgorithm):
    def __init__(self):
        super(HardThreshold, self).__init__(self.__class__.__name__)

    def _calculate_compare_value(self, input_value, local_window=None, timezone=None):

        if local_window is None:
            local_window = constants.ALGORITHM_DEFAULT_HARD_THRESHOLD_LOCAL_WINDOW

        if timezone is None:
            timezone = constants.ALGORITHM_DEFAULT_HARD_THRESHOLD_TIMEZONE

        from ada_core.handler import Handler
        try:
            if type(input_value) == AlgorithmIODataType.ENTRY.value.native_type:
                compare_value = input_value.value
            elif type(input_value) == AlgorithmIODataType.TIME_SERIES.value.native_type:
                local_ts = input_value.splitByWindow(window=local_window, timezone=timezone)
                mean_handler = Handler(algorithm_name='mean', handler_input=local_ts)
                compare_value = mean_handler.get_result()
            else:
                compare_value = input_value
        except (ValueError, AttributeError, Exception) as e:
            raise exceptions.AlgorithmCalculationError("Error when calculate compare value: {}".format(e))

        return compare_value, input_value

    def _calculate_bound(self, threshold):
        return threshold

    def _run_algorithm(self, input_value, operator, threshold, local_window=None, timezone=None):

        compare_value, input_value = self._calculate_compare_value(input_value=input_value, local_window=local_window, timezone=timezone)
        bound_value = self._calculate_bound(threshold=threshold)
        refree_value = self._compare(compare_value=compare_value, bound_value=bound_value, operator=operator)

        result = {
            "output_value": refree_value,
            "extend_info": {
                "compare_value": compare_value,
                "bound_value": [bound_value],
                "enclose": True if operator in ['>=', "<="] else False
                # "enclose": True if operator in ['>=', "<="] else False,
                # "operator": operator
            }
        }

        return result

        # return self._compare(compare_value=compare_value, bound_value=bound_value, operator=operator)


class SoftThreshold(RefereeAlgorithm):
    def __init__(self):
        super(SoftThreshold, self).__init__(self.__class__.__name__)

    def _calculate_input_ts(self, input_value, local_window=None, timezone=None, benchmark_size=None, period_window=None, period_method=None):

        if local_window is None:
            local_window = constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_LOCAL_WINDOW

        if benchmark_size is None:
            benchmark_size = constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_BENCHMARK_SIZE

        if timezone is None:
            timezone = constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_TIMEZONE

        if period_window is None:
            period_window = constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_PERIOD_WINDOW

        if str(period_window)[0] == '0' or str(period_window)[:2] == '-0':
            period_window = None

        if period_method is None:
            period_method = constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_PERIOD_METHOD

        input_value = TimeSeries(input_value)

        try:
            input_value_rest = TimeSeries(input_value)
            local_ts = input_value_rest.splitByWindow(window=local_window, direct=True, timezone=timezone)
            bnckmk_ts = input_value_rest.splitByWindow(window=benchmark_size, direct=True, left_in_flag=False, timezone=timezone)

            if len(input_value_rest) > 0:
                input_value = input_value.splitByTimestamp(left=input_value_rest.end, left_in_flag=False, direct=True)
        except (ValueError, AttributeError, Exception) as e:
            raise exceptions.AlgorithmCalculationError("Error when calculate input value range: {}".format(e))

        # period process
        from ada_core.handler import Handler

        if period_window and period_method == 'seasonal_decompose':
            input_value = Handler(algorithm_name='seasonal_decompose', handler_input=input_value, params={'trend_only': True, 'is_fillna': True, 'period_window': period_window}).get_result()

        elif period_window and period_method == 'filter_by_period':
            local_ts = input_value.splitByWindow(window=local_window, direct=False, timezone=timezone)
            input_value_final = TimeSeries()
            for p_ts, p_val in local_ts.items():
                input_value_tmp = input_value.splitByTimestamp(right=p_ts, right_in_flag=True)
                input_value_tmp = Handler(algorithm_name='filter_by_period', handler_input=input_value_tmp, params={'period_window': period_window, 'timezone': timezone}).get_result()
                input_value_final.update(input_value_tmp)
            input_value = Handler(algorithm_name='sma_smoothing', handler_input=input_value_final, params={'smoothing_window':local_window, 'smoothing_direction': 'backward'}).get_result()
            # t0=time.time()
            # input_value = Handler(algorithm_name='sma_smoothing', handler_input=input_value, params={'smoothing_window':local_window}).get_result()
            # print("smoothing tc: {}".format(time.time()-t0))
            input_value = Handler(algorithm_name='filter_by_period', handler_input=input_value, params={'period_window': period_window, 'timezone': timezone}).get_result()
        else:
            pass

        return input_value

    def _calculate_compare_value(self, input_value, local_window=None, timezone=None, benchmark_size=None,
                                 period_window=None, period_method=None, is_input_processed=False):

        if local_window is None:
            local_window = constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_LOCAL_WINDOW

        if benchmark_size is None:
            benchmark_size = constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_BENCHMARK_SIZE

        if timezone is None:
            timezone = constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_TIMEZONE

        if period_window is None:
            period_window = constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_PERIOD_WINDOW

        if str(period_window)[0] == '0' or str(period_window)[:2] == '-0':
            period_window = None

        if period_method is None:
            period_method = constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_PERIOD_METHOD

        from ada_core.handler import Handler
        input_value = TimeSeries(input_value)

        if not is_input_processed:
            input_value = self._calculate_input_ts(input_value, local_window=local_window, timezone=timezone,
                                                   benchmark_size=benchmark_size, period_window=period_window,
                                                   period_method=period_method)
        else:
            pass

        try:
            if period_window and period_method=='filter_by_period':
                local_ts = input_value.splitByWindow(window='1', direct=True, timezone=timezone)
            else:
                local_ts = input_value.splitByWindow(window=local_window, direct=True, timezone=timezone)
            mean_handler = Handler(algorithm_name='mean', handler_input=local_ts)
            compare_value = mean_handler.get_result()
        except (ValueError, AttributeError, Exception) as e:
            raise exceptions.AlgorithmCalculationError("Error when calculate compare value: {}".format(e))

        return compare_value, input_value

    def _calculate_bound(self, input_value, operator, factor=None, local_window=None, benchmark_size=None, benchmark_method=None,
                       bound_method=None, timezone=None, period_window=None, period_method=None, is_input_processed=False):

        if operator in ['>', '>=']:
            sign = 1
        else:
            sign = -1

        if local_window is None:
            local_window = constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_LOCAL_WINDOW

        if benchmark_size is None:
            benchmark_size = constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_BENCHMARK_SIZE

        if benchmark_method is None:
            benchmark_method = constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_BENCHMARK_METHOD

        if bound_method is None:
            bound_method = constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_BOUND_METHOD

        if factor is None:
            factor = constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_FACTOR

        if timezone is None:
            timezone = constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_TIMEZONE

        if period_window is None:
            period_window = constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_PERIOD_WINDOW

        if str(period_window)[0] == '0' or str(period_window)[:2] == '-0':
            period_window = None

        if period_method is None:
            period_method = constants.ALGORITHM_DEFAULT_SOFT_THRESHOLD_PERIOD_METHOD

        from ada_core.handler import Handler

        if not is_input_processed:
            input_value = self._calculate_input_ts(input_value, local_window=local_window, timezone=timezone,
                                                   benchmark_size=benchmark_size, period_window=period_window,
                                                   period_method=period_method)
        else:
            pass

        try:
            bnckmk_ts = input_value
            bnckmk_handler = Handler(algorithm_name=benchmark_method, handler_input=bnckmk_ts)
            bnckmk_value = bnckmk_handler.get_result()
        except (ValueError, AttributeError, Exception) as e:
            raise exceptions.AlgorithmCalculationError("Error when calculate bnckmk value: {}".format(e))

        try:
            if bound_method == 'hard':
                bound_value = sign * factor + bnckmk_value
            elif bound_method == 'ratio':
                bound_value = bnckmk_value * (1 + sign * factor / 100.0)
            else:
                bound_handler = Handler(algorithm_name=bound_method, handler_input=bnckmk_ts)
                bound_value = bound_handler.get_result()
                bound_value = sign * factor * bound_value + bnckmk_value
        except (ValueError, AttributeError, Exception) as e:
            raise exceptions.AlgorithmCalculationError("Error when calculate bound value: {}".format(e))

        return bound_value

    def _run_algorithm(self, input_value, operator, factor=None, local_window=None, benchmark_size=None, benchmark_method=None,
                       bound_method=None, timezone=None, period_window=None, period_method=None):

        input_value = self._calculate_input_ts(input_value=input_value, local_window=local_window, timezone=timezone,
                                               benchmark_size=benchmark_size, period_window=period_window, period_method=period_method)

        compare_value, input_value = self._calculate_compare_value(input_value=input_value, local_window=local_window, timezone=timezone,
                                                      benchmark_size=benchmark_size, period_window=period_window,
                                                      period_method=period_method, is_input_processed=True)

        bound_value = self._calculate_bound(input_value=input_value, operator=operator, factor=factor, local_window=local_window,
                                            benchmark_size=benchmark_size, benchmark_method=benchmark_method,
                                            bound_method=bound_method, timezone=timezone, period_window=period_window,
                                            period_method=period_method, is_input_processed=True)

        refree_value = self._compare(compare_value=compare_value, bound_value=bound_value, operator=operator)

        result = {
            "output_value": refree_value,
            "extend_info": {
                "compare_value": compare_value,
                "bound_value": [bound_value],
                "enclose": True if operator in ['>=', "<="] else False
                # "enclose": True if operator in ['>=', "<="] else False,
                # "operator": operator
            }
        }

        return result


class BiSoftThreshold(BiRefereeAlgorithm):

    _soft_threshold_alg = SoftThreshold()

    def __init__(self):
        super(BiSoftThreshold, self).__init__(self.__class__.__name__)

    def _calculate_compare_value(self, input_value, local_window=None, timezone=None, benchmark_size=None,
                                 period_window=None, period_method=None, is_input_processed=False):

        return self._soft_threshold_alg._calculate_compare_value(input_value=input_value, local_window=local_window,
                                                                 timezone=timezone, benchmark_size=benchmark_size,
                                                                 period_window=period_window, period_method=period_method,
                                                                 is_input_processed=is_input_processed)

    def _calculate_upper_bound(self, input_value, enclose=None, factor=None, local_window=None, benchmark_size=None,
                               benchmark_method=None, bound_method=None, timezone=None, period_window=None,
                               period_method=None, is_input_processed=False):

        if enclose is None:
            enclose = constants.ALGORITHM_DEFAULT_BI_SOFT_THRESHOLD_ENCLOSE

        # todo: the enclose data type is not checked, a value like 'x' would be allowed, temp add mini check here
        if not isinstance(enclose, bool):
            raise exceptions.AlgorithmCalculationError("the enclose value is invalid")

        if enclose:
            operator = '>='
        else:
            operator = '>'

        return self._soft_threshold_alg._calculate_bound(input_value=input_value, operator=operator, factor=factor, local_window=local_window,
                                     benchmark_size=benchmark_size, benchmark_method=benchmark_method,
                                     bound_method=bound_method, timezone=timezone, period_window=period_window,
                                     period_method=period_method, is_input_processed=is_input_processed)

    def _calculate_lower_bound(self, input_value, enclose=None, factor=None, local_window=None, benchmark_size=None,
                               benchmark_method=None, bound_method=None, timezone=None, period_window=None,
                               period_method=None, is_input_processed=False):

        if enclose is None:
            enclose = constants.ALGORITHM_DEFAULT_BI_SOFT_THRESHOLD_ENCLOSE

        # todo: the enclose data type is not checked, a value like 'x' would be allowed, temp add mini check here
        if not isinstance(enclose, bool):
            raise exceptions.AlgorithmCalculationError("the enclose value is invalid")

        if enclose:
            operator = '<='
        else:
            operator = '<'

        return self._soft_threshold_alg._calculate_bound(input_value=input_value, operator=operator, factor=factor, local_window=local_window,
                                     benchmark_size=benchmark_size, benchmark_method=benchmark_method,
                                     bound_method=bound_method, timezone=timezone, period_window=period_window,
                                     period_method=period_method, is_input_processed=is_input_processed)

    def _run_algorithm(self, input_value, enclose=None, factor=None, local_window=None, benchmark_size=None, benchmark_method=None,
                       bound_method=None, timezone=None, period_window=None, period_method=None):

        input_value = self._soft_threshold_alg._calculate_input_ts(input_value, local_window=local_window, timezone=timezone,
                                               benchmark_size=benchmark_size, period_window=period_window, period_method=period_method)

        compare_value, input_value = self._calculate_compare_value(input_value, local_window=local_window, timezone=timezone,
                                                      benchmark_size=benchmark_size, period_window=period_window,
                                                      period_method=period_method, is_input_processed=True)

        upper_bound_value = self._calculate_upper_bound(input_value=input_value, enclose=enclose, factor=factor,
                                                        local_window=local_window, benchmark_size=benchmark_size,
                                                        benchmark_method=benchmark_method, bound_method=bound_method,
                                                        timezone=timezone, period_window=period_window,
                                                        period_method=period_method, is_input_processed=True)

        lower_bound_value = self._calculate_lower_bound(input_value=input_value, enclose=enclose, factor=factor,
                                                        local_window=local_window, benchmark_size=benchmark_size,
                                                        benchmark_method=benchmark_method, bound_method=bound_method,
                                                        timezone=timezone, period_window=period_window,
                                                        period_method=period_method, is_input_processed=True)

        refree_value = self._compare_both(compare_value=compare_value, upper_bound_value=upper_bound_value,
                                          lower_bound_value=lower_bound_value, enclose=enclose)

        result = {
            "output_value": refree_value,
            "extend_info": {
                "compare_value": compare_value,
                "bound_value": [lower_bound_value, upper_bound_value],
                "enclose": enclose
            }
        }

        return result


class CushionThreshold(RefereeAlgorithm):

    def __init__(self):
        super(CushionThreshold, self).__init__(self.__class__.__name__)

    def _calculate_compare_value(self, input_value, local_window=None, timezone=None):

        if local_window is None:
            local_window = constants.ALGORITHM_DEFAULT_CUSHION_THRESHOLD_LOCAL_WINDOW

        if timezone is None:
            timezone = constants.ALGORITHM_DEFAULT_CUSHION_THRESHOLD_TIMEZONE

        from ada_core.handler import Handler
        input_value = TimeSeries(input_value)

        try:
            local_ts = input_value.splitByWindow(window=local_window, direct=True, timezone=timezone)
            mean_handler = Handler(algorithm_name='mean', handler_input=local_ts)
            compare_value = mean_handler.get_result()
        except (ValueError, AttributeError, Exception) as e:
            raise exceptions.AlgorithmCalculationError("Error when calculate compare value: {}".format(e))

        return compare_value, input_value

    def _calculate_bound(self, input_value, operator, local_window=None, benchmark_size=None, benchmark_method=None, bound_method=None,
                       factor=None, upper_percentile=None, lower_percentile=None, timezone=None):

        from ada_core.handler import Handler

        if upper_percentile is None and lower_percentile is None:
            upper_percentile = constants.ALGORITHM_DEFAULT_CUSHION_THRESHOLD_UPPER_PERCENTILE
            lower_percentile = constants.ALGORITHM_DEFAULT_CUSHION_THRESHOLD_LOWER_PERCENTILE
        elif lower_percentile is None:
            lower_percentile = 100 - upper_percentile
        elif upper_percentile is None:
            upper_percentile = 100 - lower_percentile

        if upper_percentile < lower_percentile:
            raise exceptions.ParametersNotPassed("The upper_percentile smaller than lower_percentile")

        if operator in ['>', '>=']:
            sign = 1
        else:
            sign = -1

        if benchmark_size is None:
            benchmark_size = constants.ALGORITHM_DEFAULT_CUSHION_THRESHOLD_BENCHMARK_SIZE

        if benchmark_method is None:
            benchmark_method = constants.ALGORITHM_DEFAULT_CUSHION_THRESHOLD_BENCHMARK_METHOD

        if bound_method is None:
            bound_method = constants.ALGORITHM_DEFAULT_CUSHION_THRESHOLD_BOUND_METHOD

        if factor is None:
            factor = constants.ALGORITHM_DEFAULT_CUSHION_THRESHOLD_FACTOR

        if timezone is None:
            timezone = constants.ALGORITHM_DEFAULT_CUSHION_THRESHOLD_TIMEZONE

        try:
            bnckmk_ts = input_value.splitByWindow(window=benchmark_size, direct=False, left_in_flag=False, timezone=timezone)
            bnckmk_handler = Handler(algorithm_name=benchmark_method, handler_input=bnckmk_ts)
            bnckmk_value = bnckmk_handler.get_result()
        except (ValueError, AttributeError, Exception) as e:
            raise exceptions.AlgorithmCalculationError("Error when calculate bnckmk value: {}".format(e))

        try:
            upper_handler = Handler(algorithm_name='percentile', handler_input=bnckmk_ts, params={"percent": upper_percentile})
            upper_value = upper_handler.get_result()
            lower_handler = Handler(algorithm_name='percentile', handler_input=bnckmk_ts, params={"percent": lower_percentile})
            lower_value = lower_handler.get_result()
            if upper_value == lower_value:
                cushion_value = 0.5
            else:
                if sign < 0:
                    cushion_value = (bnckmk_value - lower_value) / (upper_value - lower_value)
                else:
                    cushion_value = (upper_value - bnckmk_value) / (upper_value - lower_value)

        except (ValueError, AttributeError, Exception) as e:
            raise exceptions.AlgorithmCalculationError("Error when calculate upper/lower value and cushion value: {}".format(e))

        try:
            bound_handler = Handler(algorithm_name=bound_method, handler_input=bnckmk_ts)
            base_bound_value = bound_handler.get_result()
        except (ValueError, AttributeError, Exception) as e:
            raise exceptions.AlgorithmCalculationError("Error when calculate base bound valuee: {}".format(e))

        try:
            if sign < 0:
                bound_value = sign * factor * base_bound_value * cushion_value + lower_value
            else:
                bound_value = sign * factor * base_bound_value * cushion_value + upper_value
        except (ValueError, AttributeError, Exception) as e:
            raise exceptions.AlgorithmCalculationError("Error when calculate bound value: {}".format(e))

        return bound_value

    def _run_algorithm(self, input_value, operator, local_window=None, benchmark_size=None, benchmark_method=None, bound_method=None,
                       factor=None, upper_percentile=None, lower_percentile=None, timezone=None):

        compare_value, input_value = self._calculate_compare_value(input_value=input_value, local_window=local_window, timezone=timezone)

        bound_value = self._calculate_bound(input_value=input_value, operator=operator, local_window=local_window, benchmark_size=benchmark_size,
                                            benchmark_method=benchmark_method, bound_method=bound_method, factor=factor,
                                            upper_percentile=upper_percentile, lower_percentile=lower_percentile, timezone=timezone)

        refree_value = self._compare(compare_value=compare_value, bound_value=bound_value, operator=operator)

        result = {
            "output_value": refree_value,
            "extend_info": {
                "compare_value": compare_value,
                "bound_value": [bound_value],
                "enclose": True if operator in ['>=', "<="] else False,
                "operator": operator

            }
        }

        return result

        # return self._compare(compare_value=compare_value, bound_value=bound_value, operator=operator)


class BiCushionThreshold(BiRefereeAlgorithm):

    _cushion_alg = CushionThreshold()

    def __init__(self):
        super(BiCushionThreshold, self).__init__(self.__class__.__name__)

    def _calculate_compare_value(self, input_value, local_window=None, timezone=None):

        return self._cushion_alg._calculate_compare_value(input_value=input_value, local_window=local_window,
                                                          timezone=timezone)

    def _calculate_upper_bound(self, input_value, enclose=None, local_window=None, benchmark_size=None, benchmark_method=None, bound_method=None,
                       factor=None, upper_percentile=None, lower_percentile=None, timezone=None):

        if enclose is None:
            enclose = constants.ALGORITHM_DEFAULT_BI_CUSHION_THRESHOLD_ENCLOSE

        # todo: the enclose data type is not checked, a value like 'x' would be allowed, temp add mini check here
        if not isinstance(enclose, bool):
            raise exceptions.AlgorithmCalculationError("the enclose value is invalid")

        if enclose:
            operator = '>='
        else:
            operator = '>'

        return self._cushion_alg._calculate_bound(input_value=input_value, operator=operator, local_window=local_window,
                                     benchmark_size=benchmark_size, benchmark_method=benchmark_method, bound_method=bound_method,
                                     factor=factor, upper_percentile=upper_percentile, lower_percentile=lower_percentile, timezone=timezone)

    def _calculate_lower_bound(self, input_value, enclose=None, local_window=None, benchmark_size=None, benchmark_method=None, bound_method=None,
                       factor=None, upper_percentile=None, lower_percentile=None, timezone=None):

        if enclose is None:
            enclose = constants.ALGORITHM_DEFAULT_BI_CUSHION_THRESHOLD_ENCLOSE

        # todo: the enclose data type is not checked, a value like 'x' would be allowed, temp add mini check here
        if not isinstance(enclose, bool):
            raise exceptions.AlgorithmCalculationError("the enclose value is invalid")

        if enclose:
            operator = '<='
        else:
            operator = '<'

        return self._cushion_alg._calculate_bound(input_value=input_value, operator=operator, local_window=local_window,
                                     benchmark_size=benchmark_size, benchmark_method=benchmark_method, bound_method=bound_method,
                                     factor=factor, upper_percentile=upper_percentile, lower_percentile=lower_percentile, timezone=timezone)

    def _run_algorithm(self, input_value, enclose=None, local_window=None, benchmark_size=None, benchmark_method=None, bound_method=None,
                       factor=None, upper_percentile=None, lower_percentile=None, timezone=None):

        compare_value, input_value = self._calculate_compare_value(input_value=input_value, local_window=local_window, timezone=timezone)

        upper_bound_value = self._calculate_upper_bound(input_value=input_value, enclose=enclose, local_window=local_window,
                                     benchmark_size=benchmark_size, benchmark_method=benchmark_method, bound_method=bound_method,
                                     factor=factor, upper_percentile=upper_percentile, lower_percentile=lower_percentile, timezone=timezone)

        lower_bound_value = self._calculate_lower_bound(input_value=input_value, enclose=enclose, local_window=local_window,
                                     benchmark_size=benchmark_size, benchmark_method=benchmark_method, bound_method=bound_method,
                                     factor=factor, upper_percentile=upper_percentile, lower_percentile=lower_percentile, timezone=timezone)

        refree_value = self._compare_both(compare_value=compare_value, upper_bound_value=upper_bound_value,
                                  lower_bound_value=lower_bound_value, enclose=enclose)

        result = {
            "output_value": refree_value,
            "extend_info": {
                "compare_value": compare_value,
                "bound_value": [lower_bound_value, upper_bound_value],
                "enclose": enclose
            }
        }

        return result
        #
        # return self._compare_both(compare_value=compare_value, upper_bound_value=upper_bound_value,
        #                           lower_bound_value=lower_bound_value, enclose=enclose)
