import pytest
import numpy as np
import drdigit.digit_filtering as dfr
import pandas as pd
from drdigit import filter, filter_df


@pytest.mark.digit_filtering
def test_filter_groups():

    ids = np.array([1, 1, 1, 2, 2])
    values = [[5, 6, 7, 8, 9], [7, 6, 5, 9, 8]]

    assert all(dfr._filter_groups(
        group_ids=ids, min_len=2,
        values=values, min_value=6
    ) == [False, False, False, True, True])

    assert all(dfr._filter_groups(
        group_ids=ids, min_len=3,
        values=values, min_value=5,
    ) == [True, True, True, False, False])

    assert all(dfr._filter_groups(
        group_ids=ids, min_len=1,
    ) == [True, True, True, True, True])

    assert all(dfr._filter_groups(
        group_ids=ids, min_len=4,
    ) == [False, False, False, False, False])


@pytest.mark.digit_filtering
def test_filter_values():
    assert all(
        dfr._filter_values(
            np.array([[1, 3, 5, 1, 4]]),
        3) == [False, True, True, False, True]
    )


# TODO: make this a parametrized test
@pytest.mark.digit_filtering
def test_filter():
    group_ids = np.array(
        [1, 1, 1, 2, 2]
    )
    values = np.array([
        [2, 1, 2, 5, 6],
        [2, 3, 2, 6, 7],
    ])

    res = filter(
        group_ids=group_ids,
        values=values,
        min_value=10
    )
    assert all(res == [False] * 5)

    res = filter(
        group_ids=group_ids,
        values=values,
        min_value=0
    )
    assert all(res == [True] * 5)

    res = filter(
        group_ids=group_ids,
        values=values,
        min_value=3
    )
    assert all(res == [False, False, False, True, True])

    res = filter(
        group_ids=group_ids,
        values=values,
        min_group_size=3,
    )
    assert all(res == [True, True, True, False, False])

    res = filter(
        group_ids=group_ids,
        values=values,
        min_group_size=3,
        min_value=2
    )
    assert all(res == [True, False, True, False, False])

    res = filter(
        group_ids=group_ids,
        values=values,
        min_value=2,
        entire_groups=True,
    )
    assert all(res == [False, False, False, True, True])

    res = filter(
        group_ids=group_ids,
        values=values,
        min_value=6,
        entire_groups=True,
    )
    assert all(res == [False, False, False, False, False])

    res = filter(
        values=values,
        min_value=6,
    )
    assert all(res == [False, False, False, False, True])


@pytest.mark.digit_filtering
def test_filter_df():
    df = pd.DataFrame(dict(
        group_id=[2, 2, 1, 1, 1, 3, 3, 3],
        value1=[2, 1, 2, 5, 6, 5, 5, 5],
        value2=[2, 3, 2, 6, 7, 5, 5, 5],
    ))
    res = filter_df(df, "group_id", ["value1", "value2"], 6, 3)
    assert len(res) == 1
    assert all(res["group_id"] == [1])
