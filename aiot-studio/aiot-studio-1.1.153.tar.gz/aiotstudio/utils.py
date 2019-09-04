from __future__ import absolute_import

from datetime import datetime
from dateutil.tz import tz


def now():
    # type: () -> datetime
    """
    Returns a datetime object containing the date of execution in the UTC time zone

    If the code is run in a scheduled context (e.g. scheduled notebooks or scheduled analytics), this returns the
    *scheduled date* of the execution (regardless of when the execution is actually run).
    For example: if the code is scheduled to be run every week in the America/Montreal time zone, now() might
    return 2019-04-08 04:00:00.000000 which is a Monday, at midnight EST, expressed in the UTC time zone.

    Otherwise (no schedule context), this returns the current time in the UTC time zone.

    >>> from aiotstudio import utils
    >>> str(utils.now())
    '2018-01-01 12:13:14.456789'
    """

    # this public implementation is not meant to be run in a scheduled context, it thus always return the current time in UTC
    return datetime.now(tz.tzutc())
