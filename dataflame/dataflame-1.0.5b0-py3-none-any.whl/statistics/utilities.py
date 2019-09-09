__title__ = 'Project DataFlame'
__author__ = 'Shayan Fazeli'
__email__ = 'shayan@cs.ucla.edu'
__credit__ = 'erLab - University of California, Los Angeles'

"""
    DataFlame: Utilities for Statistical Analysis
    ==========
    This module includes the main utilities that are to be used for statistical analysis of dataframes.
"""
from typing import Tuple, Union, List
import pandas
import numpy


def compute_correlations_in_dataframe(
        dataframe: pandas.DataFrame,
        correlation_method: str = 'pearson',
        return_type: str = 'matrix',
        take_care_of_nans: bool = True
) -> Union[pandas.DataFrame, Tuple[numpy.ndarray, List[str]]]:
    """
    The :meth:`compute_correlations_in_dataframe` computes the cross correlations for all couples of features.
    It is the caller's responsibility to restructure a minimal dataframe that meets their needs.

    Parameters
    ----------
    dataframe: The input dataframe
    correlation_method: the method used for correlation: "pearson", "kendall", or "spearman"
    return_type: "matrix" or "dataframe"
    take_care_of_nans: deciding whether or not to remove nans and substitute them with 0.0

    Returns
    ----------
    If the `type` variable is set to `matrix`, it will return an instance of `numpy.ndarray` and the labels, otherwise,
    it returns an instance of `pandas.DataFrame` with the requested information in it.
    """
    correlations_dataframe = dataframe.corr(method=correlation_method)

    if return_type == 'matrix':
        correlation_labels = correlations_dataframe.columns.tolist()
        if take_care_of_nans:
            correlations_matrix = numpy.nan_to_num(correlations_dataframe.to_numpy())
        else:
            correlations_matrix = correlations_dataframe.to_numpy()
        return correlations_matrix, correlation_labels
    elif return_type == 'dataframe':
        if take_care_of_nans:
            correlations_dataframe = correlations_dataframe.fillna(value=0.0)
        return correlations_dataframe
    else:
        raise Exception('unknown return type')