"""
Author: qiacai
"""

from datetime import timedelta, datetime
import pytz
from dateutil.relativedelta import relativedelta
from ada_core import constants


def window2unix(window):
    window_str = str(window)
    end_str = window_str[-1]
    if end_str in ['s', 'm', 'h', 'd', 'w', 'M', 'y']:
        try:
            num = abs(int(window[:-1]))
            if num == 0:
                return 0
        except RuntimeError:
            raise ValueError('input ts or window is not valid')
        if end_str =='m':
            return num * 60
        elif end_str=='h':
            return num * 60 * 60
        elif end_str=='d':
            return num * 60 * 60 * 24
        elif end_str=='w':
            return num * 60 * 60 * 24 * 7
        elif end_str=='M':
            raise ValueError('no enough info to support month level transit')
        elif end_str=='y':
            raise ValueError('no enough info to support year level transit')
        else: #end_str=='y':
            return num
    else:
        try:
            return abs(int(window_str))
        except RuntimeError:
            raise ValueError('input window is not valid')


def window2timestamplite(input_stamp, window, timezone=None, always_sub=False):

    if timezone is None:
        timezone = constants.ALGORITHM_DEFAULT_TIMEZONE

    window_str = str(window)
    end_str = window_str[-1]
    if end_str in ['s', 'm', 'h', 'd', 'w', 'M', 'y']:
        try:
            if not always_sub:
                num = int(window[:-1])
            else:
                num = -abs(int(window[:-1]))
            if num == 0:
                return input_stamp
        except RuntimeError:
            raise ValueError('input timestamp or window is not valid')
        time_stamp = datetime.fromtimestamp(input_stamp, tz=pytz.timezone(timezone))
        if end_str == 'y':
             time_stamp = time_stamp+relativedelta(years=num)
        elif end_str =='m':
            time_stamp = time_stamp+relativedelta(minutes=num)
        elif end_str=='h':
            time_stamp = time_stamp+relativedelta(hours=num)
        elif end_str=='d':
            time_stamp = time_stamp+relativedelta(days=num)
        elif end_str=='w':
            time_stamp = time_stamp+relativedelta(weeks=num)
        elif end_str=='M':
            time_stamp = time_stamp+relativedelta(months=num)
        else:
            time_stamp = time_stamp+relativedelta(seconds=num)

        return int(time_stamp.timestamp())

    else:
        raise ValueError('input window is not valid')


def window2timestamp(ts, window, input_stamp=None, timezone=None, always_sub=False, error_expose=False):

    if input_stamp is None:
        input_stamp = ts.end
        if not always_sub:
            raise ValueError('When timestamp not provided, always_sub should be true')
        always_sub = True

    if timezone is None:
        timezone = constants.ALGORITHM_DEFAULT_TIMEZONE

    window_str = str(window)
    end_str = window_str[-1]
    if end_str in ['s', 'm', 'h', 'd', 'w', 'M', 'y']:

        timestamp = window2timestamplite(input_stamp, window, timezone, always_sub)
        if error_expose:
            if timestamp > ts.end:
                raise ValueError('out of right bound')
            if timestamp < ts.start:
                raise ValueError('out of left bound')
            # if timestamp > ts.end or timestamp < ts.start:
            #     raise ValueError('out of bound')
        else:
            timestamp = max(timestamp, ts.start)
            timestamp = min(timestamp, ts.end)
    else:
        try:
            window = int(window)
        except ValueError:
            raise ValueError('input window is not valid')

        if always_sub:
            window = -abs(window)
        keyList = list(ts.getKeyList())
        ts_idx = keyList.index(input_stamp)
        ts_idx = ts_idx + window
        if error_expose:
            if ts_idx < 0:
                raise ValueError('out of left bound')
            if ts_idx > len(keyList)-1:
                raise ValueError('out of right bound')
        else:
            ts_idx = max(ts_idx, 0)
            ts_idx = min(ts_idx, len(keyList)-1)
        timestamp = keyList[ts_idx]

    return timestamp