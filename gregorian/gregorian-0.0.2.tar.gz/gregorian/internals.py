import datetime
import pandas as pd

def isdatelike(value):
    """
    Returns whether a given value has a date-like interface
    """
    if isinstance(value, (datetime.date, datetime.datetime, pd.Timestamp)):
        return True
    return False

def convert(value, dtype):
    """
    Casts a value into another data type
    """
    if isinstance(value, dtype):
        return value
    if dtype == pd.Timestamp:
        return pd.Timestamp(value)
    if dtype == datetime.date:
        if isinstance(value, (pd.Timestamp, datetime.datetime)):
            return value.date()
        raise TypeError(f"Unexpected type {type(value)}")
    if dtype == datetime.datetime: 
        if isinstance(value, pd.Timestamp):
            return value.to_pydatetime()
        if isinstance(value, datetime.date): 
            datetime.datetime(value.year, value.month, value.day)
        raise TypeError(f"Unexpected type {type(value)}")
    raise ValueError("Unexpected dtype")
    