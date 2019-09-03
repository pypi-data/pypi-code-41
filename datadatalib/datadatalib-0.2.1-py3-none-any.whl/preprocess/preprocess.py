import numpy as np
from numpy import ndarray
from typing import Dict, Any, Callable
import statsmodels.api as sm
import pandas as pd


def _get_z_scores(
    x: pd.DataFrame, 
    window: int,
    min_periods: int,
    reduce_func: str,
    center: bool,
    win_type: str
) -> np.ndarray:

    reduce_mapping = {
        'median': lambda x: x.median(),
        'mean': lambda x: x.mean()
    }

    r = x.rolling(
        window=window,
        win_type=win_type,
        center=center,
        min_periods=min_periods
    )
    means = reduce_mapping[reduce_func](r)
    stds = r.std(ddof=0)

    z_scores = (x - means) / (stds + 1e-6)
    return z_scores


def remove_outliers(
    df: pd.DataFrame,
    window_size: int,
    sigma_threshold: int = 3,
    min_periods: int = 1,
    reduce_func: str = 'median',
    return_z_scores: bool = False,
    center: bool = False,
    win_type: str = None
) -> pd.DataFrame:
    """
        Remove outliers using z-score.

        Inputs:
        - df: DataFrame with columns where outliers will be removed.
        - window_size: Sliding window size to calculate z-score.
        - sigma_threshold: point will be removed if |z-score| > sigma_threshold.
        - min_periods: Minimum number of observations in window required 
            to have a value (otherwise result is NA).
        - reduce_func: Function to calculate mean. Can be mean or median.
        - return_z_scores: Whether to return z-scores.
        - center: Set the labels at the center of the window.
        - win_type: Provide a window type. If None, all points are evenly weighted. 
        See the pandas docs for further information.
    """

    # Get z-scores
    z_scores = _get_z_scores(
        df,
        window_size,
        min_periods,
        reduce_func,
        center,
        win_type
    )

    # Filter points where z_score > sigma_threshold
    df_no_outliers = df.mask(
        abs(z_scores) > sigma_threshold,
        np.nan
    )

    if return_z_scores:
        return df_no_outliers, z_scores
    
    return df_no_outliers


def fill_blanks(
    df: pd.DataFrame,
    method: str = 'ff'
) -> pd.DataFrame:
    """
        Fill NA values.

        Inputs:
        - df: DataFrame with columns to fill.
        - method: Filling strategy. 
            ff -> forward fill
            li -> linear interpolation
            zeros -> fill with zeros
    """

    strategy_mapping = {
        'ff': lambda df: df.fillna(method='ffill'),
        'li': lambda df: df.interpolate(),
        'zeros': lambda df: df.fillna(0)
    }

    if method not in strategy_mapping.keys():
        raise ValueError(f'method: {method} unknown')

    return strategy_mapping[method](df)


def _single_exp_smooth(
    s: pd.Series,
    alpha: float
) -> pd.Series:

    x = np.zeros(len(s))
    x[0] = s[0]
    for i in range(1, len(s)):
        x[i] = alpha * s[i] + (1- alpha)*x[i-1]
    
    return pd.Series(x, index=s.index)


def _double_exp_smooth(
    s: pd.Series,
    alpha: float,
    beta: float
) -> pd.Series:

    x = np.zeros(len(s))
    x[0] = s[0]
    b = s[1] - s[0]

    for i in range(1, len(s)):
        x[i] = alpha * s[i] + (1- alpha)*(x[i-1] + b)
        b = beta*(x[i] - x[i-1]) + (1-beta)*b
    
    return pd.Series(x, index=s.index)


def smooth_noise_exponential(
    s: pd.Series,
    method: str = 'single_exp',
    alpha: float = 0.95,
    beta: float = 0.3
) -> pd.Series:
    """
        Smooth time series applying exponential smoothing.

        Inputs:
        - s: pandas.Series to smooth.
        - method: Smoothing method. 
            single_exp -> simple exponential smoothing
            double_exp -> double exponential smoothing
    """

    if method == 'single_exp':
        return _single_exp_smooth(s, alpha)
    elif method == 'double_exp':
        return _double_exp_smooth(s, alpha, beta)
    
    raise ValueError(f'method: {method} unknown')


def smooth_noise_mean(
    series: pd.Series,
    window_size: int,
    center: bool = False,
    win_type: str = None,
    closed: str = None,
    std: float = None
) -> pd.Series:
    """
        Smooth time series applying rolling mean smoothing.

        Inputs:
        - s: pandas.Series to smooth.
        - window_size: Rolling window size.
        - center: Whether to set the smoothed values at the center of the window.
        - win_type: Provide a window type. If None, all points are evenly weighted. 
        See pandas docs for further information.
        - closed: Make the interval closed on the ‘right’, ‘left’, ‘both’ or ‘neither’ endpoints.
        - std: Used only for gaussian window.
    """

    smoothed = series.rolling(
        window=window_size,
        min_periods=1,
        center=center,
        win_type=win_type,
        closed=closed
    ).mean(std=std)

    return smoothed


def smooth_noise_lowess(
    series: pd.Series,
    frac: float = 1/3,
    it: float = 3,
    delta: float = 0
) -> pd.Series:
    """
        Smooth time series applying LOWESS smoothing.

        Inputs:
        - series: pandas.Series to smooth.
        - frac: Between 0 and 1. The fraction of the data used when estimating each value.
        - it: The number of residual-based reweightings to perform.
        - delta: Distance within which to use linear-interpolation instead of weighted regression.
    """

    lowess = sm.nonparametric.lowess
    smoothed: np.ndarray = lowess(
        series.values, 
        series.index,
        frac=frac, 
        it=it,
        delta=delta,
        return_sorted = False
    )
    
    return pd.Series(smoothed, index=series.index)


def smooth_noise(
    series: pd.Series,
    method: str = 'exponential',
    params: Dict[str, Any] = {}
) -> pd.Series:
    """
        Smooth time series applying available methods.

        Inputs:
        - series: pandas.Series to smooth.
        - method: Method to use. 'exponential', 'rolling_mean' or 'lowess' available.
        - params: Parameters specific for certain method.
    """

    smooth_mapping: Dict[str, Callable] = {
        'exponential': smooth_noise_exponential,
        'rolling_mean': smooth_noise_mean,
        'lowess': smooth_noise_lowess
    }

    if method not in smooth_mapping.keys():
        raise ValueError(f'method: {method} unknown')
    
    smoothed = smooth_mapping[method](series, **params)

    return smoothed