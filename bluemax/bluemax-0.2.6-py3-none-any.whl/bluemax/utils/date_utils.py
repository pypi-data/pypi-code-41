# pylint: disable=W0703,R1710
""" Useful with dates """
import datetime


def json_date(date):
    """ javascript hates a t """
    if date:
        return date.isoformat().replace("T", " ")


def parse_date(value):  # noqa: 901
    """
        Returns a Python datetime.datetime object,
        the input must be in some date ISO format
    """
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value
    result = None
    if value:
        try:
            result = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
        except Exception:
            try:
                result = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
            except Exception:
                try:
                    result = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    result = datetime.datetime.strptime(value, "%Y-%m-%d")
    return result


def parse_unix_time(value):
    """ can never remeber how to get back from javascript """
    return datetime.datetime.fromtimestamp(float(value))
