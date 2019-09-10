# coding: utf-8
import time
import datetime


def get_timestamp(t=None, ms=False):
    if t is not None:
        if isinstance(t, datetime.datetime):
            t = time.mktime(t.timetuple())
        elif isinstance(t, str):
            t = time.mktime(datetime.datetime.strptime(t, '%Y-%m-%d %H:%M:%S').timetuple())
    else:
        t = time.time()

    if ms:
        return int(t * 1000)
    return int(t)


def timestamp_to_datetime(ts, ms=False, to_str=False, format='%Y-%m-%d %H:%M:%S'):
    if ms:
        ts = ts / 1000.0
    dt = datetime.datetime.fromtimestamp(ts)
    if to_str:
        return dt.strftime(format)
    return dt
