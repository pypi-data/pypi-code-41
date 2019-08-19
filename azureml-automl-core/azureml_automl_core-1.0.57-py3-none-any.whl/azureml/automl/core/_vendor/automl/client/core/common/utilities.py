# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility methods for validation and conversion."""
from typing import Any, cast, Dict, List, Optional, Tuple, Union

import json
import re
import traceback
import warnings
import logging
import numpy as np
import pandas as pd
import pandas.api as api
import scipy
from math import sqrt

from automl.client.core.common import constants
from automl.client.core.common.constants import NumericalDtype, DatetimeDtype
from automl.client.core.common.exceptions import DataException, AutoMLException, ErrorTypes
from automl.client.core.common.forecasting_exception import (AzureMLForecastException,
                                                             classify_forecasting_exception)
from automl.client.core.common.types import DataInputType
from sklearn import model_selection


# For backward compatibility

SOURCE_WRAPPER_MODULE = 'automl.client.core.common.model_wrappers'
MAPPED_WRAPPER_MODULE = 'azureml.train.automl.model_wrappers'


def _check_if_column_data_type_is_numerical(data_type_as_string: str) -> bool:
    """
    Check if column data type is numerical.

    Arguments:
        data_type_as_string {string} -- string carrying the type from infer_dtype().

    Returns:
        bool -- 'True' if the dtype returned is 'integer', 'floating', 'mixed-integer' or 'mixed-integer-float'.
                     'False' otherwise.

    """
    if data_type_as_string in list(NumericalDtype.FULL_SET):
        return True

    return False


def _check_if_column_data_type_is_datetime(data_type_as_string: str) -> bool:
    """
    Check if column data type is datetime.

    Arguments:
        data_type_as_string {string} -- string carrying the type from infer_dtype().

    Returns:
        bool -- 'True' if the dtype returned is 'date', 'datetime' or 'datetime64'. 'False' otherwise.

    """
    return data_type_as_string in DatetimeDtype.FULL_SET


def _check_if_column_data_type_is_int(data_type_as_string: str) -> bool:
    """
    Check if column data type is integer.

    Arguments:
        data_type_as_string {string} -- string carrying the type from infer_dtype().

    Returns:
        boolean -- 'True' if the dtype returned is 'integer'. 'False' otherwise.

    """
    if data_type_as_string == NumericalDtype.Integer:
        return True

    return False


def get_value_int(intstring: str) -> Optional[Union[int, str]]:
    """
    Convert string value to int.

    Arguments:
        intstring {str} -- The input value to be converted.

    Returns:
        int -- The converted value.

    """
    if intstring is not None and intstring != '':
        return int(intstring)
    return intstring


def get_value_float(floatstring: str) -> Optional[Union[float, str]]:
    """
    Convert string value to float.

    Arguments:
        floatstring {str} -- The input value to be converted.

    Returns:
        float -- The converted value.

    """
    if floatstring is not None and floatstring != '':
        return float(floatstring)
    return floatstring


def get_value_from_dict(dictionary: Dict[str, Any], names: List[str], default_value: Any) -> Any:
    """
    Get the value of a configuration item that has a list of names.

    Arguments:
        dictionary {dict} -- Dictionary of settings with key value pair to look the data for.
        names {list of str} -- The list of names for the item looking foi.
        default_value {object} -- Default value to return if no matching key found

    Returns:
        object -- Returns the first value from the list of names.

    """
    for key in names:
        if key in dictionary:
            return dictionary[key]
    return default_value


def _get_indices_missing_labels_output_column(y: DataInputType) -> np.ndarray:
    """
    Return the indices of missing values in y.

    :param y: Array of training labels
    :return: Array of indices in y where the value is missing
    """
    if np.issubdtype(y.dtype, np.number):
        return np.argwhere(np.isnan(y)).flatten()
    else:
        # Cast needed as numpy-stubs thinks None is not an allowed input to np.where
        return np.argwhere((y == "nan") | np.equal(y, cast(np.ndarray, None))).flatten()


def _y_nan_check(output: Dict[str, Union[pd.DataFrame, np.array]]) -> \
        Dict[str, Optional[Union[np.array, List[str], float, List[int]]]]:
    """
    Check for nans in y.

    Keyword Arguments:
        output {dict} -- dictionary containing the output to check. (default: {None})

    Raises:
        DataException -- All label data is NaN.

    Returns:
        dict -- dictionary containing checked output.

    """
    y = output['y']
    X = output['X']
    sample_weight = output['sample_weight']
    if y is not None and pd.isnull(y).any():
        warnings.warn(
            "Labels contain NaN values. Removing for AutoML Experiment.")
        y_indices_pruned = ~pd.isnull(y)
        X_reduced = X[y_indices_pruned]
        y_reduced = y[y_indices_pruned]
        sample_weight_reduced = None
        if sample_weight is not None:
            sample_weight_reduced = sample_weight[y_indices_pruned]
        if y_reduced.shape[0] == 0:
            raise DataException('All label data is NaN.')
        output['X'] = X_reduced
        output['y'] = y_reduced
        output['sample_weight'] = sample_weight_reduced
    y_valid = output['y_valid']
    X_valid = output['X_valid']
    sample_weight_valid = output['sample_weight_valid']
    if y_valid is not None and pd.isnull(y_valid).any():
        warnings.warn(
            "Validation Labels contain NaN values. "
            "Removing for AutoML Experiment.")
        y_valid_indices_pruned = ~pd.isnull(y_valid)
        X_valid_reduced = X_valid[y_valid_indices_pruned]
        y_valid_reduced = y_valid[y_valid_indices_pruned]
        sample_weight_valid_reduced = None
        if sample_weight_valid is not None:
            sample_weight_valid_reduced = \
                sample_weight_valid[y_valid_indices_pruned]
        output['X_valid'] = X_valid_reduced
        output['y_valid'] = y_valid_reduced
        output['sample_weight_valid'] = sample_weight_valid_reduced
    return output


def _log_traceback(exception: Exception, logger: logging.Logger) -> None:
    """
    Log traceback exception.

    Arguments:
        exception {Error} -- exception to log traceback for.
        logger {logger} -- logger to log traceback in.

    """
    logger.error(exception)
    logger.error(traceback.format_exc())


def _get_column_data_type_as_str(array):
    """
    Get the type of ndarray by looking into the ndarray contents.

    :param array: ndarray
    :raise ValueError if array is not ndarray or not valid
    :return: type of column as a string (integer, floating, string etc.)
    """
    # If the array is not valid, then throw exception
    if array is None:
        raise DataException("The input array is None")

    # If the array is not an instance of ndarray, then throw exception
    if not isinstance(array, np.ndarray):
        raise DataException("Not an instance of ndarray")

    # Ignore the Nans and then return the data type of the column
    return api.types.infer_dtype(array[~pd.isnull(array)])


def _check_dimensions(
        X, y, X_valid, y_valid, sample_weight, sample_weight_valid):
    """
    Check dimensions of data inputs.

    Arguments:
        X {numpy.ndarray} -- X.
        y {numpy.ndarray} -- y.
        X_valid {numpy.ndarray} -- X for validation.
        y_valid {numpy.ndarray} -- y for validation.
        sample_weight {numpy.ndarray} -- sample weight for training.
        sample_weight_valid {numpy.ndarray} -- sample weight for validation.

    """
    dimension_error_message = "Dimension mismatch for {0} data. " \
                              "Expecting {1} dimensional array, " \
                              "but received {2} dimensional data."
    feature_dimensions = 2
    label_dimensions = 1

    # if the data is not in these 4 type, we will bypass the test
    x_dim = None
    y_dim = None
    x_valid_dim = None
    y_valid_dim = None
    sample_weight_dim = None
    sample_weight_valid_dim = None
    x_shape = None
    y_shape = None
    x_valid_shape = None
    y_valid_shape = None
    sample_weight_shape = None
    sample_weight_valid_shape = None

    if X is not None and (isinstance(X, pd.DataFrame) or isinstance(X, np.ndarray) or scipy.sparse.issparse(X)):
        x_shape = X.shape
        x_dim = X.ndim

    if X_valid is not None and \
            (isinstance(X_valid, pd.DataFrame) or isinstance(X_valid, np.ndarray) or scipy.sparse.issparse(X_valid)):
        x_valid_shape = X_valid.shape
        x_valid_dim = X_valid.ndim

    if isinstance(y, pd.DataFrame) or scipy.sparse.issparse(y):
        y_shape = y.shape
        y_dim = y.shape[1]
    elif isinstance(y, np.ndarray):
        y_shape = y.shape
        y_dim = y.ndim

    if isinstance(y_valid, pd.DataFrame) or scipy.sparse.issparse(y_valid):
        y_valid_shape = y_valid.shape
        y_valid_dim = y_valid.shape[1]
    elif isinstance(y_valid, np.ndarray):
        y_valid_shape = y_valid.shape
        y_valid_dim = y_valid.ndim

    if isinstance(sample_weight, pd.DataFrame) or scipy.sparse.issparse(sample_weight):
        sample_weight_shape = sample_weight.shape
        sample_weight_dim = sample_weight.shape[1]
    elif isinstance(sample_weight, np.ndarray):
        sample_weight_shape = sample_weight.shape
        sample_weight_dim = sample_weight.ndim

    if isinstance(sample_weight_valid, pd.DataFrame) or scipy.sparse.issparse(sample_weight_valid):
        sample_weight_valid_shape = sample_weight_valid.shape
        sample_weight_valid_dim = sample_weight_valid.shape[1]
    elif isinstance(sample_weight_valid, np.ndarray):
        sample_weight_valid_shape = sample_weight_valid.shape
        sample_weight_valid_dim = sample_weight_valid.ndim

    if x_dim is not None and x_dim > feature_dimensions:
        raise DataException(
            dimension_error_message
            .format("X", feature_dimensions, x_dim))
    if y_dim is not None and y_dim != label_dimensions:
        raise DataException(
            dimension_error_message
            .format("y", label_dimensions, y_dim))
    if x_valid_dim is not None and x_valid_dim > feature_dimensions:
        raise DataException(
            dimension_error_message
            .format("X_valid", feature_dimensions, x_valid_dim))
    if y_valid_dim is not None and y_valid_dim != label_dimensions:
        raise DataException(
            dimension_error_message
            .format("y_valid", label_dimensions, y_valid_dim))
    if sample_weight_dim is not None and sample_weight_dim != label_dimensions:
        raise DataException(
            dimension_error_message
            .format("sample_weight", label_dimensions, sample_weight_dim))
    if sample_weight_valid_dim is not None and sample_weight_valid_dim != label_dimensions:
        raise DataException(
            dimension_error_message.format(
                "sample_weight_valid", label_dimensions, sample_weight_valid_dim))

    if x_shape is not None and y_shape is not None and x_shape[0] != y_shape[0]:
        raise DataException(
            "X and y data do not have the same number of samples. "
            "X has {0} samples and y has {1} samples."
            .format(x_shape[0], y_shape[0]))
    if x_valid_shape is not None and y_valid_shape is not None and \
            x_valid_shape[0] != y_valid_shape[0]:
        raise DataException(
            "X_valid and y_valid data do not have the same number "
            "of samples. X_valid has {0} samples and "
            "y_valid has {1} samples."
            .format(x_valid_shape[0], y_valid_shape[0]))
    if sample_weight_shape is not None and y_shape is not None and \
            sample_weight_shape[0] != y_shape[0]:
        raise DataException(
            "sample_weight and y data do not have the same number "
            "of samples. sample_weight has {0} samples and "
            "y has {1} samples."
            .format(sample_weight_shape[0], y_shape[0]))
    if sample_weight_valid_shape is not None and y_valid_shape is not None and\
            sample_weight_valid_shape[0] != y_valid_shape[0]:
        raise DataException(
            "sample_weight_valid and y_valid data do not have the same number "
            "of samples. sample_weight_valid has {0} samples and y_valid "
            "has {1} samples.".format(sample_weight_valid_shape[0], y_valid_shape[0]))
    if x_shape is not None and y_shape is not None and x_shape[0] == 0:
        raise DataException("X and y data do not have any samples.")
    if x_valid_shape is not None and y_valid_shape is not None and x_valid_shape[0] == 0:
        raise DataException("X_valid and y_valid data do not have any samples.")


def _get_max_min_comparator(objective):
    """Return a comparator either maximizing or minimizing two values. Will not handle nans."""
    if objective == constants.OptimizerObjectives.MAXIMIZE:
        def maximize(x, y):
            if x >= y:
                return x
            else:
                return y
        return maximize
    elif objective == constants.OptimizerObjectives.MINIMIZE:
        def minimize(x, y):
            if x <= y:
                return x
            else:
                return y
        return minimize
    else:
        raise ValueError(
            "Maximization or Minimization could not be determined "
            "based on current metric.")


def sparse_std(x):
    """
    Compute the std for a sparse matrix.

    Std is computed by dividing by N and not N-1 to match numpy's computation.

    :param x: sparse matrix
    :return: std dev
    """
    if not scipy.sparse.issparse(x):
        raise ValueError("x is not a sparse matrix")

    mean_val = x.mean()
    num_els = x.shape[0] * x.shape[1]
    nzeros = x.nonzero()
    sum = mean_val**2 * (num_els - nzeros[0].shape[0])
    for i, j in zip(*nzeros):
        sum += (x[i, j] - mean_val)**2

    return sqrt(sum / num_els)


def sparse_isnan(x):
    """
    Return whether any element in matrix is nan.

    :param x: sparse matrix
    :return: True/False
    """
    if not scipy.sparse.issparse(x):
        raise ValueError("x is not sparse matrix")

    for i, j in zip(*x.nonzero()):
        if np.isnan(x[i, j]):
            return True

    return False


def subsampling_recommended(num_samples):
    """
    Return whether or not subsampling is recommended for the current scenario.

    Arguments:
        num_samples {int} -- number of samples.

    Returns:
        bool -- True if subsampling is recommended, else False.

    """
    return num_samples >= 50000


def stratified_shuffle(indices, y, random_state):
    """
    Shuffle an index in a way such that the first 1%, 2%, 4% etc. are all stratified samples.

    The way we achieve this is, first get 1:99 split
    then for the 99 part, we do a split of 1:98
    and then in the 98 part, we do a split of 2:96
    and then in the 96 part, we split 4:92
    then 8:86
    then 16:70
    then 32:38

    Arguments:
        indices {numpy.ndarray} -- indices to shuffle.
        y {numpy.ndarray} -- field to stratify by.
        random_state {RandomState, int, NoneType} -- random_state for random operations.

    Returns:
        numpy.ndarray -- shuffled indices.

    """
    if y is None:
        # no stratification required
        indices_copy = np.array(indices)
        old_state = np.random.get_state()
        np.random.seed(random_state or 0)
        np.random.shuffle(indices_copy)
        np.random.set_state(old_state)
        return indices_copy

    splits = [
        [1, 99],
        [1, 98],
        [2, 96],
        [4, 92],
        [8, 86],
        [16, 70],
        [32, 38]]

    ret = np.array([])
    y_left = y

    for split in splits:
        kept_frac = float(split[0]) / (split[0] + split[1])
        kept, left = model_selection.train_test_split(
            indices,
            train_size=kept_frac,
            stratify=y_left,
            random_state=random_state)
        ret = np.concatenate([ret, kept])
        indices = left
        y_left = y[left]

    ret = np.concatenate([ret, left]).astype('int')
    return ret


def _log_raw_data_stat(raw_feature_stats, logger=None, prefix_message=None):
    if logger is None:
        return
    if prefix_message is None:
        prefix_message = ""
    raw_feature_stats_dict = dict()
    for name, stats in raw_feature_stats.__dict__.items():
        try:
            stats_json_str = json.dumps(stats)
        except (ValueError, TypeError):
            stats_json_str = json.dumps(dict())
        raw_feature_stats_dict[name] = stats_json_str
    logger.info(
        "{}RawFeatureStats:{}".format(
            prefix_message, json.dumps(raw_feature_stats_dict)
        )
    )


def _get_ts_params_dict(automl_settings: Any) -> Optional[Dict[str, str]]:
    """
    Get time series parameter data.

    Arguments:
        automl_settings {AutoMLSettings} -- automl settings object

    Returns:
        dict -- a dictionary of time series data info

    """
    if automl_settings.is_timeseries:
        dict_time_series = {
            constants.TimeSeries.TIME_COLUMN_NAME: automl_settings.time_column_name,
            constants.TimeSeries.GRAIN_COLUMN_NAMES: automl_settings.grain_column_names,
            constants.TimeSeries.DROP_COLUMN_NAMES: automl_settings.drop_column_names,
            constants.TimeSeriesInternal.OVERWRITE_COLUMNS: automl_settings.overwrite_columns,
            constants.TimeSeriesInternal.DROP_NA: automl_settings.dropna,
            constants.TimeSeriesInternal.TRANSFORM_DICT: automl_settings.transform_dictionary,
            constants.TimeSeries.MAX_HORIZON: automl_settings.max_horizon,
            constants.TimeSeriesInternal.ORIGIN_TIME_COLUMN_NAME:
                constants.TimeSeriesInternal.ORIGIN_TIME_COLNAME_DEFAULT,
            constants.TimeSeries.COUNTRY_OR_REGION: automl_settings.country_or_region,
            constants.TimeSeriesInternal.CROSS_VALIDATIONS: automl_settings.n_cross_validations,
            constants.TimeSeries.SHORT_SERIES_HANDLING: automl_settings.short_series_handling
        }
        # Set window size and lags only if user did not switched it off by setting to None.
        if automl_settings.window_size is not None:
            dict_time_series[constants.TimeSeriesInternal.WINDOW_SIZE] = automl_settings.window_size
        if automl_settings.lags is not None:
            dict_time_series[constants.TimeSeriesInternal.LAGS_TO_CONSTRUCT] = automl_settings.lags
        if hasattr(automl_settings, constants.TimeSeries.SEASONALITY):
            dict_time_series[constants.TimeSeries.SEASONALITY] = \
                getattr(automl_settings, constants.TimeSeries.SEASONALITY)
        if hasattr(automl_settings, constants.TimeSeries.USE_STL):
            dict_time_series[constants.TimeSeries.USE_STL] = \
                getattr(automl_settings, constants.TimeSeries.USE_STL)
        return dict_time_series
    else:
        return None


def get_primary_metrics(task: str) -> List[str]:
    """
    Get the primary metrics supported for a given task as a list.

    :param task: string "classification" or "regression".
    :return: A list of the primary metrics supported for the task.
    """
    if task == constants.Tasks.CLASSIFICATION:
        return list(constants.Metric.CLASSIFICATION_PRIMARY_SET)
    elif task == constants.Tasks.REGRESSION:
        return list(constants.Metric.REGRESSION_PRIMARY_SET)
    else:
        raise NotImplementedError("Task {task} is not supported currently."
                                  .format(task=task))


def convert_dict_values_to_str(input_dict: Dict[Any, Any]) -> Dict[str, str]:
    """
    Convert a dictionary's values so that every value is a string.

    :param input_dict: the dictionary that should be converted
    :return: a dictionary with all values converted to strings
    """
    fit_output_str = {}
    for key in input_dict:
        if input_dict[key] is None:
            fit_output_str[str(key)] = ''
        else:
            # Cast to string to avoid warnings (PR 143137)
            fit_output_str[str(key)] = str(input_dict[key])
    return fit_output_str


def to_ordinal_string(integer: int) -> str:
    """
    Convert an integer to an ordinal string.

    :param integer:
    :return:
    """
    return "%d%s" % (integer, "tsnrhtdd"[(integer / 10 % 10 != 1) * (integer % 10 < 4) * integer % 10::4])


def check_input(df: pd.DataFrame) -> None:
    """
    Check inputs for transformations.

    :param df: Input dataframe.
    :return:
    """
    # Raise an exception if the input is not a data frame or array
    if not isinstance(df, pd.DataFrame) and not isinstance(df, np.ndarray):
        raise ValueError("df should be a pandas dataframe or numpy array")


# Regular expressions for date time detection
date_regex1 = re.compile(r'(\d+/\d+/\d+)')
date_regex2 = re.compile(r'(\d+-\d+-\d+)')


def is_known_date_time_format(datetime_str: str) -> bool:
    """
    Check if a given string matches the known date time regular expressions.

    :param datetime_str: Input string to check if it's a date or not
    :return: Whether the given string is in a known date time format or not
    """
    if date_regex1.search(datetime_str) is None and date_regex2.search(datetime_str) is None:
        return False

    return True


def build_run_failure_error_detail(exception: BaseException) -> str:
    """
    Build the run failure error detail from the exception.

    :param exception: The exception that fails the run.
    :return: Return the str containing exception class and exception type.
    """
    msg = "Message hidden."
    if isinstance(exception, AutoMLException):
        msg = str(exception)
    error_type = get_error_code(exception)
    return "[{}][{}]{}".format(exception.__class__.__name__, error_type, msg)


def get_error_code(exception: BaseException) -> str:
    """
    Build the error code from an exception.

    :param exception: The exception that fails the run.
    :return: Return the str containing error_code.
    """
    error_code = ErrorTypes.Unclassified
    if isinstance(exception, AutoMLException):
        error_code = exception.get_error_type()
    elif isinstance(exception, AzureMLForecastException):
        error_code = classify_forecasting_exception(exception)
        error_code = getattr(exception, "_error_code", error_code)
    return str(error_code)


def get_min_points(window_size: int, lags: List[int], max_horizon: int, cv: Optional[int]) -> int:
    """
    Return the minimum number of data points needed for training.

    :param window_size: the rolling window size.
    :param lags: The lag size.
    :param max_horizon: the desired length of forecasting.
    :param cv: the number of cross validations.
    :return: the minimum number of data points.
    """
    min_points = max_horizon + max(window_size, max(lags)) + 1
    if cv is not None:
        min_points = min_points + cv + max_horizon
    return min_points
