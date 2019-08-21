"""
Author: qiacai
"""

from collections import OrderedDict
from schematics.exceptions import ConversionError, BaseError, CompoundError
from collections import Mapping
import numpy as np
import logging
from ada_core import constants

from ada_core.data_model.entry import Entry

from ada_core import utils, exceptions

logger = logging.getLogger(__name__)


class TimeSeries(OrderedDict):

    def __init__(self, data=None):
        super(TimeSeries, self).__init__()

        if data is not None:
            self.load_data(data)

    @property
    def start(self):
        """
        Return the earliest timestamp in the ts
        :return: int
        """
        return min(self.keys()) if self.keys() else None

    @property
    def end(self):
        """
        Return the latest timestamp in the ts
        :return: int
        """
        return max(self.keys()) if self.keys() else None

    def __repr__(self):
        return 'TimeSeries<start={0}, end={1}>'.format(repr(self.start), repr(self.end))

    def __str__(self):
        """
        :return string: Return string representation of time series
        """
        string_rep = ''
        for item in self.items():
            if not string_rep:
                string_rep += str(item)
            else:
                string_rep += ', ' + str(item)
        return 'TimeSeries([{}])'.format(string_rep)

    def getEntryList(self):
        entryList = []
        for key, value in self.items():
            entryList.append(Entry(key, value))
        return entryList

    def getValueList(self):
        return list(self.values())

    def getKeyList(self):
        return list(self.keys())

    def popEntry(self, key=None):
        if key is None:
            key = max(self.keys())
        entry = Entry(key, self.get(key))
        self.pop(key)
        return entry

    def splitByTimestamp(self, left=None, left_in_flag=True, right=None, right_in_flag=True, direct=False):
        if len(self) <= 0:
            raise ValueError('the timeseries is not long enough for split')

        if left is None and right is None:
            raise ValueError('the start point and end point could not both be null')

        if left is None:
            left = self.start

        if right is None:
            right = self.end

        ret_ts = {}
        keyList = list(self.keys())

        if left_in_flag:
            keyList = [keya for keya in keyList if keya >= left]
        else:
            keyList = [keya for keya in keyList if keya > left]

        if right_in_flag:
            keyList = [keya for keya in keyList if keya <= right]
        else:
            keyList = [keya for keya in keyList if keya < right]

        for keya in keyList:
            ret_ts.update({keya: self.get(keya)})
            if direct:
                self.pop(keya)
        return TimeSeries(ret_ts)

    def splitByWindow(self, window, timestamp=None, direct=False, left_in_flag=False, right_in_flag=True, timezone=None):

        if timestamp is None:
            timestamp = self.end
            always_sub = True
        else:
            always_sub = False

        if len(self) <= 0:
            raise ValueError('the timeseries is not long enough for split')

        try:
            timestamp_ts = utils.window2timestamp(self, window, timestamp, timezone, always_sub, error_expose=True)
        except ValueError as e:
            if str(e).count('out of left bound') > 0:
                timestamp_ts = self.start
                left_in_flag = True
            elif str(e).count('out of right bound') > 0:
                timestamp_ts = self.end
                right_in_flag = True
            else:
                raise exceptions.AlgorithmCalculationError(e)

        if timestamp >= timestamp_ts:
            return self.splitByTimestamp(left=timestamp_ts, left_in_flag=left_in_flag, right=timestamp, right_in_flag=right_in_flag, direct=direct)
        else:
            return self.splitByTimestamp(left=timestamp, left_in_flag=left_in_flag, right=timestamp_ts, right_in_flag=right_in_flag, direct=direct)

    def timeOffset(self, offset_window=0, timezone=None):

        output_value = TimeSeries()
        try:
            offset_window = int(offset_window)
            offset_window = str(offset_window) + 's'
        except ValueError:
            pass
        for timestamp, value in self.items():
            timestamp_set = utils.window2timestamplite(timestamp, offset_window, timezone, always_sub=False)
            output_value.update({timestamp_set: value})
        return output_value

    def filterByPeriod(self, period_window='1', align_point='end', direct=False, timezone=None):

        if period_window is None:
            period_window = '1'
        if align_point is None:
            align_point = 'end'
        if direct is None:
            direct = False
        if timezone is None:
            timezone = constants.ALGORITHM_DEFAULT_TIMEZONE

        output_ts = dict()
        if align_point == 'end':
            # run the filter from end
            temp_timestamp = self.end
            output_ts.update({self.end: self.get(self.end)})
            while temp_timestamp > self.start:
                try:
                    temp_timestamp = utils.window2timestamp(self, period_window, input_stamp=temp_timestamp,
                                                            timezone=timezone, always_sub=True, error_expose=True)
                    if temp_timestamp >= self.end:
                        return self
                except ValueError as e:
                    if str(e).count('out of left bound') > 0:
                        break
                    else:
                        raise exceptions.AlgorithmCalculationError(e)
                if self.get(temp_timestamp) is not None:
                    output_ts.update({temp_timestamp: self.get(temp_timestamp)})
                    if direct:
                        self.pop(temp_timestamp)

        elif align_point == 'start':
            # run the filter from start
            if period_window[0] == '-':
                period_window = period_window[1:]

            temp_timestamp = self.start
            output_ts.update({self.start: self.get(self.start)})
            while temp_timestamp < self.end:
                try:
                    temp_timestamp = utils.window2timestamp(self, period_window, input_stamp=temp_timestamp,
                                                            timezone=timezone, always_sub=False, error_expose=True)
                    if temp_timestamp <= self.start:
                        return self
                except ValueError as e:
                    if str(e).count('out of right bound') > 0:
                        break
                    else:
                        raise exceptions.AlgorithmCalculationError(e)
                if self.get(temp_timestamp) is not None:
                    output_ts.update({temp_timestamp: self.get(temp_timestamp)})
                    if direct:
                        self.pop(temp_timestamp)
        else:
            raise ValueError('the parameter "align_point" only support "end / start"')

        return TimeSeries(output_ts)

    def load_data(self, value):

        if not isinstance(value, Mapping):
            raise ConversionError('Only mappings may be used to load TimeSeries')

        errors = {}
        for k in sorted(value.keys()):
            try:
                self.update({int(k): float(value.get(k))})
            except (BaseError, ValueError) as exc:
                errors[k] = exc
                continue
        if errors:
            if len(self) < 1 or (len(self) == 1 and len(self) < len(value)):
                logger.error('The time series did not have enough valid element')
                raise CompoundError(errors)
            else:
                logger.warning('Data filtered due to errors:')
                for e in errors:
                    logger.warning('({}:{})'.format(e, errors[e]))

    def equals(self, other):
        if not isinstance(other, TimeSeries):
            return False
        left_key_set = set(self.getKeyList())
        right_key_set = set(other.getKeyList())
        if len(left_key_set.difference(right_key_set)) > 0:
            return False
        for timestamp, value in self.items():
            if value != other.get(timestamp):
                return False
            else:
                continue
        return True

    def _op_ts(self, other, op, fill_value):

        def run_op(a, b, op):
            if op in ['add', 'radd']:
                return a + b
            elif op == 'sub':
                return a - b
            elif op == 'rsub':
                return b - a
            elif op in ['mul', 'rmul']:
                return a * b
            elif op == 'truediv':
                return a / b
            elif op == 'rtruediv':
                return b / a
            elif op == 'floordiv':
                return a // b
            elif op == 'rfloordiv':
                return b // a
            elif op == 'mod':
                return a % b
            elif op == 'rmod':
                return b % a
            elif op == 'pow':
                return a ** b
            elif op == 'eq':
                return float(a == b)
            elif op == "gt":
                return float(a > b)
            elif op == "ge":
                return float(a >= b)
            elif op == "lt":
                return float(a < b)
            elif op == "le":
                return float(a <= b)
            else:
                raise ValueError('unknown op')

        if not (isinstance(fill_value, int) or isinstance(fill_value, float)) and fill_value is not None:
            raise ValueError("fill_value should be numeric")

        output_value = TimeSeries()
        if isinstance(other, int) or isinstance(other, float):
            for timestamp, value in self.items():
                output_value.update({timestamp: run_op(value, other, op)})
            return output_value

        elif isinstance(other, TimeSeries):
            keyList = self.getKeyList() + other.getKeyList()
            keyList = sorted(list(set(keyList)))
            for key in keyList:
                value_left = self.get(key)
                value_right = other.get(key)
                if fill_value is None:
                    value_combine = run_op(value_left, value_right, op) if (value_left is not None and value_right is not None) else None
                else:
                    value_combine = run_op((value_left if value_left is not None else fill_value), (value_right if value_right is not None else fill_value), op)

                if value_combine is None:
                    continue
                else:
                    output_value.update({key: value_combine})
            return output_value
        else:
            raise ValueError("could only work with numeric value or TimeSeries")

    def add(self, other, fill_value=None):
        return self._op_ts(other, 'add',  fill_value)

    def __add__(self, other):
        return self.add(other)

    def radd(self, other, fill_value=None):
        return self._op_ts(other, 'radd',  fill_value)

    def __radd__(self, other):
        return self.radd(other)

    def sub(self, other, fill_value=None):
        return self._op_ts(other, 'sub',  fill_value)

    def __sub__(self, other):
        return self.sub(other)

    def rsub(self, other, fill_value=None):
        return self._op_ts(other, 'rsub',  fill_value)

    def __rsub__(self, other):
        return self.rsub(other)

    def mul(self, other, fill_value=None):
        return self._op_ts(other, 'mul',  fill_value)

    def __mul__(self, other):
        return self.mul(other)

    def rmul(self, other, fill_value=None):
        return self._op_ts(other, 'rmul',  fill_value)

    def __rmul__(self, other):
        return self.rmul(other)

    def truediv(self, other, fill_value=None):
        return self._op_ts(other, 'truediv',  fill_value)

    def __truediv__(self, other):
        return self.truediv(other)

    def rtruediv(self, other, fill_value=None):
        return self._op_ts(other, 'rtruediv',  fill_value)

    def __rtruediv__(self, other):
        return self.rtruediv(other)

    def floordiv(self, other, fill_value=None):
        return self._op_ts(other, 'floordiv',  fill_value)

    def __floordiv__(self, other):
        return self.floordiv(other)

    def rfloordiv(self, other, fill_value=None):
        return self._op_ts(other, 'rfloordiv',  fill_value)

    def __rfloordiv__(self, other):
        return self.rfloordiv(other)

    def mod(self, other, fill_value=None):
        return self._op_ts(other, 'mod',  fill_value)

    def __mod__(self, other):
        return self.mod(other)

    def rmod(self, other, fill_value=None):
        return self._op_ts(other, 'rmod',  fill_value)

    def __rmod__(self, other):
        return self.rmod(other)

    def pow(self, other, fill_value=None):
        return self._op_ts(other, 'pow',  fill_value)

    def __pow__(self, other):
        return self.pow(other)

    def eq(self, other, fill_value=None):
        return self._op_ts(other, 'eq', fill_value)

    def __eq__(self, other):
        return self.eq(other)

    def gt(self, other, fill_value=None):
        return self._op_ts(other, 'gt', fill_value)

    def __gt__(self, other):
        return self.gt(other)

    def greaterThan(self, other):
        return True if sum(self.gt(other).getValueList()) >= len(other) else False

    def ge(self, other, fill_value=None):
        return self._op_ts(other, 'ge', fill_value)

    def __ge__(self, other, fill_value=None):
        return self.ge(other)

    def greaterThanOrEquals(self, other):
        return True if sum(self.ge(other).getValueList()) >= len(other) else False

    def lt(self, other, fill_value=None):
        return self._op_ts(other, 'lt', fill_value)

    def __lt__(self, other):
        return self.lt(other)

    def lessThan(self, other):
        return True if sum(self.lt(other).getValueList()) >= len(other) else False

    def le(self, other, fill_value=None):
        return self._op_ts(other, 'le', fill_value)

    def __le__(self, other):
        return self.le(other)

    def lessThanOrEquals(self, other):
        return True if sum(self.le(other).getValueList()) >= len(other) else False

    def __neg__(self):
        output_value = TimeSeries()
        for timestamp, value in self.items():
                output_value.update({timestamp: -value})
        return output_value

    def __pos__(self):
        output_value = TimeSeries()
        for timestamp, value in self.items():
                output_value.update({timestamp: +value})
        return output_value

    def __abs__(self):
        output_value = TimeSeries()
        for timestamp, value in self.items():
                output_value.update({timestamp: abs(value)})
        return output_value

    def __round__(self, ndigits=0):
        output_value = TimeSeries()
        for timestamp, value in self.items():
                output_value.update({timestamp: round(value, ndigits)})
        return output_value

    def mean(self, default=None):
        return np.asscalar(np.average(self.getValueList())) if self.getValueList() else default

    def median(self, default=None):
        return np.asscalar(np.median(self.getValueList())) if self.getValueList() else default

    def max(self, default=None):
        return np.asscalar(np.max(self.getValueList())) if self.getValueList() else default

    def min(self, default=None):
        return np.asscalar(np.min(self.getValueList())) if self.getValueList() else default

    def std(self, default=None):
        return np.asscalar(np.std(self.getValueList())) if self.getValueList() else default

    def mad(self, default=None):
        if self.getValueList():
            median_value = np.asscalar(np.median(self.getValueList()))
            median_diff_list = [np.asscalar(np.abs(x - median_value)) for x in self.getValueList()]
            return np.asscalar(np.median(median_diff_list))
        else:
            return default

    def count(self, default=None):
        return len(self.getValueList()) if self.getValueList() else default

    def sum(self, default=None):
        return np.asscalar(np.sum(self.getValueList())) if self.getValueList() else default

    def __bool__(self):
        return False if not self.getKeyList() or not self.getValueList() else True