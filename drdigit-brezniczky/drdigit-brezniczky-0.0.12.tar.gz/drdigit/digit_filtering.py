from collections import OrderedDict
import numpy as np
import pandas as pd
from typing import List
from deprecation import deprecated


def _digit_noise_series(n: int) -> np.ndarray:
    # TODO: hm... random seeds?
    # TODO: not 100% about the return value type hint
    """
    Whenever the PMF of vote values is monotonously decreasing, the aggregated
    digit probability PMF is consistently decreasing too. Then when filtering
    with a minimum, the bottommost value will be overrepresented in the
    resulting sample as well as, consistently, the last digit of the minimum
    value, overrepresented in the sample.
    Adding a noise that uniformly distributes over the last digits with a mean
    zero to either side of the filtering inequality should relief such anomalies.

    :param n: number of noise samples to generate.
    :return:
    """
    return np.random.choice(range(10), n) - 4.5


@deprecated(deprecated_in="0.0.12", removed_in="0.1.0",
            details="Please use the filter and filter_df functions instead.")
def get_feasible_groups(df: pd.DataFrame, min_n_wards: int, min_votes: int,
                        value_colname: str="Fidesz",
                        group_colname: str="Telepules",
                        smooth_ld_selectivity: bool=True) -> pd.Series:
    agg = (
        df[[group_colname, value_colname]]
        .groupby([group_colname])
        .aggregate(OrderedDict([(group_colname, len), (value_colname, min)]))
    )
    min_value_colname = "min_%s_votes" % value_colname
    agg.columns = ["n_wards", min_value_colname]
    agg = agg.reset_index()

    vote_mins = agg[min_value_colname]
    if smooth_ld_selectivity:
        vote_mins += _digit_noise_series(len(agg))

    return agg.loc[(agg.n_wards >= min_n_wards) &
                   (vote_mins >= min_votes)][group_colname]


@deprecated(deprecated_in="0.0.12", removed_in="0.1.0",
            details="Please use the filter and filter_df functions instead.")
def get_feasible_rows(df: pd.DataFrame, min_value: int,
                      min_value_col_idxs: List[int],
                      smooth_ld_selectivity: bool=True) -> pd.DataFrame:
    """
    Filter row by row for eligible values, but ignore the settlement ward
    counts. Can be useful for taking a look at areas with very few wards.

    :param df: Data frame to filter.
    :param min_value: Rows with with each interesting column containing at least
        this many votes will be returned.
    :param min_value_col_idxs: Interesting columns specified by a list-like of
        indexes.
    :param smooth_ld_selectivity: Whether to use smoothing to avoid the
        potential digit-specificity of the filter value to a degree.
    :return: The filtered data frame.
    """
    if smooth_ld_selectivity:
        min_value = _digit_noise_series(len(df)) + min_value
    is_okay = df.iloc[:, min_value_col_idxs].apply(min, axis=1) >= min_value
    return df[is_okay]


def _filter_values(values: List[np.ndarray], min_value: int):
    ans = [act_values >= min_value for act_values in values]
    return np.logical_and.reduce(ans)


def _filter_groups(group_ids: np.ndarray, min_len: int=None,
                   values: np.ndarray=[], min_value: int=None):

    if len(values) == 0:
        # special case - nothing to do in this respect
        min_value = None

    df = pd.DataFrame(dict(id=group_ids))
    if min_value:
        df["value"] = np.amin(values, axis=0)

    aggregation_dict = {}
    if min_len:
        aggregation_dict["id"] = len
    if min_value:
        aggregation_dict["value"] = min

    df = df.groupby(["id"]).aggregate(aggregation_dict)

    v = []
    if min_len:
        v.append(df["id"] >= min_len)
    if min_value:
        v.append(df["value"] >= min_value)

    groups = df[np.logical_and.reduce(v)].index

    return np.isin(group_ids, groups)


def filter(group_ids: np.ndarray=None,
           values: List[np.ndarray]=None,
           entire_groups=False,
           min_value: int=None,
           min_group_size: int=None) -> np.ndarray:
    """
    :param group_ids: Group id values (~ contents of a 'column').
    :param values: An array-like of arrays of (scalar) values to be filtered.
        Each should be as long as the group_ids (~ each is a 'column').
    :param min_value: Minimum value to expect from any item (row or group)
        passing the filter in the values.
    :param min_group_size: Minimum group length.
    :param entire_groups: Whether groups partly matching the conditions
        (value >= min_value), i.e. not for all rows, are to be excluded.
    :return: The filter (one boolean for each 'row', i.e. a 'column').
    """
    ans = []

    if values is None:
        values = []

    if entire_groups:
        return _filter_groups(group_ids, min_group_size, values, min_value)

    if min_group_size:
        ans.append(_filter_groups(group_ids, min_group_size))
    if min_value:
        ans.append(_filter_values(values, min_value))
        
    return np.logical_and.reduce(ans)


def filter_df(df: pd.DataFrame,
              group_column: str=None,
              value_columns: List[str]=None,
              min_value: int=None,
              min_group_size: int=None,
              entire_groups=False) -> pd.DataFrame:
    """
    Convenience wrapper around the filter() function to apply its concepts to a
    data frame.
    See also: filter()

    :param df: Data frame to be filtered.
    :param group_column: Column containing group ids.
    :param value_columns: Names of columns containing values. Use it in 
        conjunction with the min_value argument.  
    :param min_value: Minimum value to expect from any item (row or group) 
        passing the filter in the value columns.
    :param min_group_size: Minimum group length.
    :param entire_groups: Whether groups partly matching the conditions
        (value >= min_value), i.e. not for all rows, are to be excluded.
    :return: The filtered data frame.
    """
    group_ids = df[group_column] if group_column is not None else None
    values = ([df[value_column] for value_column in value_columns]
              if value_columns is not None
              else None)
    f = filter(group_ids=group_ids, values=values,
               entire_groups=entire_groups, min_value=min_value,
               min_group_size=min_group_size) 
    return df[f]


# def get_feasible_subseries(arr, min_votes):
#     # TODO: here's a one (0.5?) off error, well done ;) it goes -5 to 4 - fix it
#     arr = arr[arr >= (min_votes - 5) + np.random.choice(range(10), len(arr))]
#     return arr


# if __name__ == "__main__":
