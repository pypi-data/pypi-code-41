import pytest

import pandas as pd
import numpy as np

from seeq import spy
from seeq.sdk.rest import ApiException

from . import test_common


def setup_module():
    test_common.login()


@pytest.mark.system
def test_pull_signal_with_grid():
    search_results = spy.search({
        "Path": "Example >> Cooling Tower 1 >> Area A"
    })

    search_results = search_results.loc[
        search_results['Name'].isin(['Compressor Power', 'Compressor Stage'])]

    df = spy.pull(search_results, start='2019-01-01', end='2019-03-07', grid='5min', header='Name',
                  tz_convert='US/Central')

    # We assert an exact value here to draw attention to any changes. The only reason this number should change is if
    # the Example Data changes in some way or there is a (possibly unexpected) change to Spy.
    assert len(df) == 18721

    # Note that the canonical timezone for US/Central appears to be CST
    assert df.index[0].tzname() == 'CST'

    assert isinstance(df.iloc[0]['Compressor Power'], np.float64)
    assert isinstance(df.iloc[0]['Compressor Stage'], np.str)


@pytest.mark.system
def test_pull_signal_no_grid():
    # This test ensures that time series with non-matching timestamps are returned
    # in a DataFrame with index entries properly interleaved and NaNs where one
    # series has a value and one doesn't.

    data1_df = spy.push(pd.DataFrame({'test_pull_signal_no_grid_1': [1, 2, 3]},
                                     index=[
                                         pd.to_datetime('2019-01-01T00:00:00.000Z'),
                                         pd.to_datetime('2019-01-01T01:00:00.000Z'),
                                         pd.to_datetime('2019-01-01T02:00:00.000Z'),
                                     ]))

    data2_df = spy.push(pd.DataFrame({'test_pull_signal_no_grid_2': [10, 20, 30]},
                                     index=[
                                         pd.to_datetime('2019-01-01T00:10:00.000Z'),
                                         pd.to_datetime('2019-01-01T01:10:00.000Z'),
                                         pd.to_datetime('2019-01-01T02:10:00.000Z'),
                                     ]))

    data3_df = spy.push(pd.DataFrame({'test_pull_signal_no_grid_3': [100, 200, 300]},
                                     index=[
                                         pd.to_datetime('2019-01-01T00:20:00.000Z'),
                                         pd.to_datetime('2019-01-01T01:20:00.000Z'),
                                         pd.to_datetime('2019-01-01T02:20:00.000Z'),
                                     ]))

    all_df = data1_df.append(data2_df).append(data3_df)

    pull_df = spy.pull(all_df, start='2018-12-01', end='2019-12-01', grid=None)

    expected_df = pd.DataFrame({
        'test_pull_signal_no_grid_1': [1, np.nan, np.nan, 2, np.nan, np.nan, 3, np.nan, np.nan],
        'test_pull_signal_no_grid_2': [np.nan, 10, np.nan, np.nan, 20, np.nan, np.nan, 30, np.nan],
        'test_pull_signal_no_grid_3': [np.nan, np.nan, 100, np.nan, np.nan, 200, np.nan, np.nan, 300]
    }, index=[
        pd.to_datetime('2019-01-01T00:00:00.000Z'),
        pd.to_datetime('2019-01-01T00:10:00.000Z'),
        pd.to_datetime('2019-01-01T00:20:00.000Z'),
        pd.to_datetime('2019-01-01T01:00:00.000Z'),
        pd.to_datetime('2019-01-01T01:10:00.000Z'),
        pd.to_datetime('2019-01-01T01:20:00.000Z'),
        pd.to_datetime('2019-01-01T02:00:00.000Z'),
        pd.to_datetime('2019-01-01T02:10:00.000Z'),
        pd.to_datetime('2019-01-01T02:20:00.000Z')
    ])

    assert pull_df.equals(expected_df)


@pytest.mark.system
def test_bad_timezone():
    with pytest.raises(RuntimeError):
        spy.pull(pd.DataFrame(), tz_convert='CDT')


@pytest.mark.system
def test_no_end_date():
    search_results = spy.search({
        "Name": "Area A_Temperature"
    })

    start = pd.datetime.now() - pd.Timedelta(hours=1)
    df = spy.pull(search_results, start=start, grid=None)

    assert 28 <= len(df) <= 32


@pytest.mark.system
def test_bounding_values():
    metadata_df = pd.DataFrame([{
        'Name': 'test_bounding_values',
        'Type': 'Signal',
        'Interpolation Method': 'step'
    }], index=['test_bounding_values'])

    data_df = pd.DataFrame({'test_bounding_values': [1, 2, 3]},
                           index=[
                               pd.to_datetime('2019-01-01T00:00:00.000Z'),
                               pd.to_datetime('2019-01-01T00:01:00.000Z'),
                               pd.to_datetime('2019-01-01T00:02:00.000Z'),
                           ])

    push_df = spy.push(data=data_df, metadata=metadata_df)

    pull_df = spy.pull(push_df, start=pd.to_datetime('2019-01-01T00:00:50.000Z'),
                       end=pd.to_datetime('2019-01-01T00:01:50.000Z'), grid=None)

    expected_df = pd.DataFrame({
        'test_bounding_values': [2]
    }, index=[
        pd.to_datetime('2019-01-01T00:01:00.000Z')
    ])

    assert pull_df.equals(expected_df)

    pull_df = spy.pull(push_df, start=pd.to_datetime('2019-01-01T00:00:50.000Z'),
                       end=pd.to_datetime('2019-01-01T00:01:50.000Z'), grid=None, bounding_values=True)

    expected_df = pd.DataFrame({
        'test_bounding_values': [1, 2, 3]
    }, index=[
        pd.to_datetime('2019-01-01T00:00:00.000Z'),
        pd.to_datetime('2019-01-01T00:01:00.000Z'),
        pd.to_datetime('2019-01-01T00:02:00.000Z')
    ])

    assert pull_df.equals(expected_df)


@pytest.mark.system
def test_pull_condition_as_capsules():
    search_results = spy.search({
        'Name': 'Area A_Temperature'
    })

    push_result = spy.push(metadata=pd.DataFrame([{
        'Type': 'Condition',
        'Name': 'Hot',
        'Formula': '$a.validValues().valueSearch(isGreaterThan(80))',
        'Formula Parameters': {
            '$a': search_results.iloc[0]
        }
    }]))

    spy.pull(push_result.iloc[0], start='2019-01-01T00:00:00.000Z', end='2019-06-01T00:00:00.000Z')


@pytest.mark.system
def test_pull_condition_as_signal():
    search_results = spy.search({
        'Name': 'Area A_Temperature'
    })

    push_result = spy.push(metadata=pd.DataFrame([{
        'Type': 'Condition',
        'Name': 'Hot',
        'Formula': '$a.validValues().valueSearch(isGreaterThan(80))',
        'Formula Parameters': {
            '$a': search_results.iloc[0]
        }
    }]))

    spy.pull(push_result.iloc[0], start='2019-01-01T00:00:00.000Z', end='2019-06-01T00:00:00.000Z',
             capsules_as='signals')


@pytest.mark.system
def test_pull_swapped_condition():
    search_results = spy.search({
        'Name': 'Temperature',
        'Path': 'Example >> Cooling Tower 1 >> Area A'
    })

    push_result = spy.push(metadata=pd.DataFrame([{
        'Type': 'Signal',
        'Name': 'Temperature Minus 5',
        'Formula': '$a - 5',
        'Formula Parameters': {
            '$a': search_results.iloc[0]
        }
    }]))

    push_result = spy.push(metadata=pd.DataFrame([{
        'Type': 'Condition',
        'Name': 'Cold',
        'Formula': '$a.validValues().valueSearch(isLessThan(80))',
        'Formula Parameters': {
            '$a': push_result.iloc[0]
        }
    }]))

    pull_df = spy.search({
        'Type': 'Asset',
        'Path': 'Example >> Cooling Tower 2'
    })

    # There will be an error related to trying to swap in Area F
    with pytest.raises(ApiException):
        spy.pull(pull_df, start='2019-01-01T00:00:00.000Z', end='2019-06-01T00:00:00.000Z',
                 calculation=push_result)

    df = spy.pull(pull_df, start='2019-01-01T00:00:00.000Z', end='2019-06-01T00:00:00.000Z',
                  calculation=push_result, errors='catalog')

    assert len(df) > 800

    conditions = df['Condition'].drop_duplicates().tolist()

    assert conditions == [
        'Example >> Cooling Tower 2 >> Area D',
        'Example >> Cooling Tower 2 >> Area E'
    ]
