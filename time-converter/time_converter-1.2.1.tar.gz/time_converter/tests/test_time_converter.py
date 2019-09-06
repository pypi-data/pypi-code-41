"""
This module includes tests for the time_Timeer module
"""
import pytest

from time_converter import Time
from pytest import approx, raises
import datetime as dt
import numpy as np


def test_consistency():
    assert Time(1000, 'sol').to('sol') == approx(1000)
    assert Time(dt.datetime(2018, 1, 1)).to('dt') == dt.datetime(2018, 1, 1)
    assert Time(6e8, 'sclk').to('sclk') == approx(6e8)
    assert Time((2018, 2.5), 'doy').to('doy') == (2018, 2.5)
    assert Time(2018.5, 'decimalyear').to('decimalyear') == approx(2018.5)
    assert Time(1517742867, 'posix').to('posix') == 1517742867

    ce4lst = Time((1, dt.time(8, 30)), 'ce4lst').to('ce4lst')
    assert ce4lst[0] == 1
    assert abs(dt.datetime.combine(dt.date.today(), ce4lst[1]) - dt.datetime.combine(dt.date.today(), dt.time(8, 30))) < dt.timedelta(minutes=1)


def test_values():
    time = Time(dt.datetime(2018, 1, 15))
    assert time.to('sol') == approx(1935.221950230014)
    assert time.to('sclk') == approx(569244654.78994048)
    assert time.to('doy') == (2018, approx(15))
    assert time.to('decimalyear') == approx(2018.0383561643835)
    assert time.to('posix') == 1515974400
    with pytest.raises(ValueError):
        time.to('ce4lst')

    time = Time(dt.datetime(2019, 3, 20))
    assert time.to('ce4lst') == (3, dt.time(22, 49, 2))


def test_values_reverse():
    try:
        import spiceypy as spice
    except ImportError:
        spice = None

    if spice is not None:
        assert Time((1, dt.time(0, 0)), 'ce4lst').to('dt') == dt.datetime(2018, 12, 22, 16, 25, 51, 600000)
        assert Time((1, dt.time(23, 59, 59)), 'ce4lst').to('dt') == dt.datetime(2019, 1, 21, 7, 3, 44, 200000)
        assert Time((10, dt.time(23, 59, 59)), 'ce4lst').to('dt') == dt.datetime(2019, 10, 13, 20, 50, 37, 900000)
    else:
        assert Time((1, dt.time(0, 0)), 'ce4lst').to('dt') == dt.datetime(2018, 12, 22, 16, 30)
        assert Time((1, dt.time(23, 59, 59)), 'ce4lst').to('dt') == dt.datetime(2019, 1, 21, 7, 30)


def test_empty():
    time = Time([])
    assert np.array_equal(time.to('sol'), [])


def test_error():
    with raises(ValueError):
        Time(1, 'foo')


def test_pandas():
    import pandas as pd
    series = pd.Series([1, 2])
    converted = Time(series, 'sol').to('sol')
    assert (converted == series).all()
    assert type(converted) == pd.core.series.Series
