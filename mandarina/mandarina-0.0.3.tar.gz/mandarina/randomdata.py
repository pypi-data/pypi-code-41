"""
This module contains functions to generate random data
"""

import random
import string
import datetime


def random_string(length=6, chars=string.ascii_letters):
    """
    This function generates random strings with specified lengths.

    :param length: Length of the random string
    :param chars: Charset to choose chracters from
    :return: Randomly generated string

    Example
    >>> random_string(30, string.ascii_letters + string.digits)

    """
    return "".join(random.choice(chars) for _ in range(length))


def random_datetime(start, end):
    """
    This function will return a random datetime between the range
    of two datetime objects.

    :param start: Startdate
    :param end: Enddate
    :return: A random Datetime object

    Example
    >>> from_date = datetime.datetime(year=2001, month=1, day=1)
    >>> to_date = datetime.datetime.now()
    >>> random_datetime(from_date, to_date)

    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + datetime.timedelta(seconds=random_second)

