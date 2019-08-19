# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utilities used during AutoML training."""
import warnings
from typing import Any, cast, Callable, Dict, List, Optional, Tuple, Union

import logging
import numpy as np
import pandas as pd
import scipy
from sklearn.base import TransformerMixin
from sklearn.utils import validation as sk_validation

import azureml.dataprep as dprep

from automl.client.core.common import constants
from automl.client.core.common import utilities
from automl.client.core.common._cv_splits import _CVSplits
from automl.client.core.common.cache_store import CacheStore
from automl.client.core.common.datasets import SubsampleCacheStrategy, ClientDatasets, DatasetBase
from automl.client.core.common.exceptions import DataException, ConfigException
from automl.client.core.common.forecasting_exception import (DataFrameValueException,
                                                             DataFrameFrequencyException)
from automl.client.core.common.streaming_dataset import StreamingDataset
from automl.client.core.common.time_series_data_frame import TimeSeriesDataFrame
from automl.client.core.common.types import DataInputType, DataSingleColumnInputType
from azureml.automl.core.data_context import TransformedDataContext
from . import _engineered_feature_names
from . import dataprep_utilities
from .automl_base_settings import AutoMLBaseSettings
from .data_transformation import _add_raw_column_names_to_X
from .featurizer.transformer import TimeSeriesPipelineType, TimeSeriesTransformer
from automl.client.core.common.constants import TimeSeries


class SmallDataSetLimit:
    """Constants for the small dataset limit."""

    WARNING_SIZE = 100
    TRAIN_VALID_MINIMAL_SIZE = 2


class LargeDatasetLimit:
    """Constants for limiting large datasets."""

    MAX_ROWS_TO_SUBSAMPLE = 10000


def auto_blacklist(input_data, automl_settings):
    """
    Add appropriate files to blacklist automatically.

    :param input_data:
    :param automl_settings: The settings used for this current run.
    :return:
    """
    if automl_settings.auto_blacklist:
        X = input_data['X']
        if scipy.sparse.issparse(X) or X.shape[0] > constants.MAX_SAMPLES_BLACKLIST:
            if automl_settings.blacklist_algos is None:
                automl_settings.blacklist_algos = \
                    constants.MAX_SAMPLES_BLACKLIST_ALGOS
            else:
                for blacklist_algo in constants.MAX_SAMPLES_BLACKLIST_ALGOS:
                    if blacklist_algo not in automl_settings.blacklist_algos:
                        automl_settings.blacklist_algos.append(blacklist_algo)
            automl_settings.blacklist_samples_reached = True


def set_task_parameters(y, automl_settings):
    """
    Set this task's parameters based on some heuristics if they aren't provided.

    TODO: Move this code into AutoML settings or something. Client shouldn't have to think about this stuff.

    :param automl_settings: The settings used for this current run
    :param y: The list of possible output values
    :return:
    """
    if automl_settings.task_type == constants.Tasks.CLASSIFICATION:
        #  Guess number of classes if the user did not explicitly provide it
        if not automl_settings.num_classes or not isinstance(
                automl_settings.num_classes, int):
            automl_settings.num_classes = len(np.unique(y))
        return

    if automl_settings.task_type == constants.Tasks.REGRESSION:
        numpy_unserializable_ints = (np.int8, np.int16, np.int32, np.int64,
                                     np.uint8, np.uint16, np.uint32, np.uint64)

        #  Guess min and max of y if the user did not explicitly provide it
        if not automl_settings.y_min or not isinstance(automl_settings.y_min,
                                                       float):
            automl_settings.y_min = np.min(y)
            if isinstance(automl_settings.y_min, numpy_unserializable_ints):
                automl_settings.y_min = int(automl_settings.y_min)
        if not automl_settings.y_max or not isinstance(automl_settings.y_max,
                                                       float):
            automl_settings.y_max = np.max(y)
            if isinstance(automl_settings.y_max, numpy_unserializable_ints):
                automl_settings.y_max = int(automl_settings.y_max)
        assert automl_settings.y_max != automl_settings.y_min
        return
    raise NotImplementedError()


def format_training_data(
        X=None, y=None, sample_weight=None, X_valid=None, y_valid=None, sample_weight_valid=None,
        data=None, label=None, columns=None, cv_splits_indices=None, user_script=None,
        is_adb_run=False, automl_settings=None, logger=None, verifier=None):
    """
    Create a dictionary with training and validation data from all supported input formats.

    :param X: Training features.
    :type X: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param y: Training labels.
    :type y: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param sample_weight: Sample weights for training data.
    :type sample_weight: pandas.DataFrame pr numpy.ndarray or azureml.dataprep.Dataflow
    :param X_valid: validation features.
    :type X_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param y_valid: validation labels.
    :type y_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param sample_weight_valid: validation set sample weights.
    :type sample_weight_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param data: Training features and label.
    :type data: pandas.DataFrame
    :param label: Label column in data.
    :type label: str
    :param columns: whitelist of columns in data to use as features.
    :type columns: list(str)
    :param cv_splits_indices:
        Indices where to split training data for cross validation.
        Each row is a separate cross fold and within each crossfold, provide 2 arrays,
        the first with the indices for samples to use for training data and the second
        with the indices to use for validation data. i.e [[t1, v1], [t2, v2], ...]
        where t1 is the training indices for the first cross fold and v1 is the validation
        indices for the first cross fold.
    :type cv_splits_indices: numpy.ndarray
    :param user_script: File path to script containing get_data()
    :param is_adb_run: True if this is being called from an ADB/local experiment
    :param automl_settings: automl settings
    :param logger: logger
    :param verifier: Verifier Manager instance.
    :type verifier: Optional[VerifierManager]
    :return:
    """
    data_dict = None
    x_raw_column_names = None

    if X is None and y is None and data is None:
        if data_dict is None:
            data_dict = _extract_user_data(user_script)
        X = data_dict.get('X')
        y = data_dict.get('y')
        sample_weight = data_dict.get('sample_weight')
        X_valid = data_dict.get('X_valid')
        y_valid = data_dict.get('y_valid')
        sample_weight_valid = data_dict.get('sample_weight_valid')
        cv_splits_indices = data_dict.get("cv_splits_indices")
        x_raw_column_names = data_dict.get("x_raw_column_names")
    elif data is not None and label is not None:
        # got pandas DF
        X = data[data.columns.difference([label])]
        if columns is not None:
            X = X[X.columns.intersection(columns)]
        y = data[label].values

        # Get the raw column names
        if isinstance(X, pd.DataFrame):
            # Cache the raw column names if available
            x_raw_column_names = X.columns.values
    else:
        # Get the raw column names
        if isinstance(X, pd.DataFrame):
            # Cache the raw column names if available
            x_raw_column_names = X.columns.values
        else:
            if is_adb_run:
                # Hack to make sure we get a pandas DF and not a numpy array in ADB
                # The two retrieval functions should be rationalized in future releases
                dataframe_retrieve_func = dataprep_utilities.try_retrieve_pandas_dataframe
            else:
                dataframe_retrieve_func = dataprep_utilities.try_retrieve_numpy_array
            X = dataframe_retrieve_func(X)
            y = dataprep_utilities.try_retrieve_last_col_numpy_array(y)
            sample_weight = dataprep_utilities.try_retrieve_last_col_numpy_array(
                sample_weight)
            X_valid = dataframe_retrieve_func(X_valid)
            y_valid = dataprep_utilities.try_retrieve_last_col_numpy_array(y_valid)
            sample_weight_valid = dataprep_utilities.try_retrieve_last_col_numpy_array(
                sample_weight_valid)
            cv_splits_indices = dataprep_utilities.try_resolve_cv_splits_indices(
                cv_splits_indices)
            if isinstance(X, pd.DataFrame):
                x_raw_column_names = X.columns.values

    if automl_settings is None or not automl_settings.preprocess or automl_settings.is_timeseries:
        if isinstance(X, pd.DataFrame):
            X = X.values
        if isinstance(X_valid, pd.DataFrame):
            X_valid = X_valid.values
    y = _convert_to_numpy_maybe(y, 'y')
    y_valid = _convert_to_numpy_maybe(y_valid, 'y_valid')
    if isinstance(sample_weight, pd.DataFrame):
        sample_weight = sample_weight.values
    if isinstance(sample_weight_valid, pd.DataFrame):
        sample_weight_valid = sample_weight_valid.values

    if automl_settings is not None:
        X, y, X_valid, y_valid = automl_settings.rule_based_validation(
            X=X,
            y=y,
            X_valid=X_valid,
            y_valid=y_valid,
            cv_splits_indices=cv_splits_indices,
            logger=logger,
            verifier=verifier
        )

    data_dict = {
        'X': X,
        'y': y,
        'X_valid': X_valid,
        'y_valid': y_valid,
        'cv_splits_indices': cv_splits_indices,
        'x_raw_column_names': x_raw_column_names,
        'sample_weight': sample_weight,
        'sample_weight_valid': sample_weight_valid}
    return data_dict


def _convert_to_numpy_maybe(
        y: Optional[Union[np.ndarray, pd.DataFrame, pd.Series]],
        ds_name: str) -> Optional[np.ndarray]:
    """
    Try to convert y to numpy array.

    If y can not be converted to np.ndarray or has wrong shape the DataException is raised.
    :param y: The data set to be converted.
    :param ds_name: The name of the data set to convert.
    :raises: DataException
    """
    if y is None:
        return y
    if isinstance(y, pd.DataFrame):
        _check_y_shape(y, 'y')
        return y[y.columns[0]].values
    if isinstance(y, pd.Series):
        return y.values
    return y


def _check_y_shape(y: pd.DataFrame, ds_name: str) -> None:
    """
    Check if y data frame has only one column.

    :param y: The y dataframe.
    :param name: The name of a data set.
    :raises: DataException
    """
    if y.shape[1] > 1:
        raise DataException((
            "Dimension mismatch for {} data. "
            "Expecting 1 dimensional array, "
            "but received {} dimensional data.").format(ds_name, y.shape[1]))


def validate_training_data(X: DataInputType,
                           y: DataInputType,
                           X_valid: Optional[DataInputType],
                           y_valid: Optional[DataInputType],
                           sample_weight: Optional[DataInputType],
                           sample_weight_valid: Optional[DataInputType],
                           cv_splits_indices: Optional[np.ndarray],
                           automl_settings: AutoMLBaseSettings,
                           check_sparse: bool = False,
                           logger: Optional[logging.Logger] = None) -> None:
    """
    Validate that training data and parameters have been correctly provided.

    :param X:
    :param y:
    :param X_valid:
    :param y_valid:
    :param sample_weight:
    :param sample_weight_valid:
    :param cv_splits_indices:
    :param automl_settings:
    :param check_sparse:
    """
    # if using incremental learning, validate and subsample data inputs. subsampling the input Dataflows
    # to numpy arrays this allows the validation flow (which can handle numpy arrays but not
    # Dataflows directly at the moment) to proceed.
    if automl_settings.use_incremental_learning:
        X, y, X_valid, y_valid, sample_weight, sample_weight_valid = (
            incremental_learning_validate_and_subsample_inputs(
                X, y, X_valid, y_valid, sample_weight, sample_weight_valid
            ))

    check_x_y(X, y, automl_settings, x_valid=X_valid, y_valid=y_valid,
              check_sparse=check_sparse, logger=logger)

    # Ensure at least one form of validation is specified
    if not ((X_valid is not None) or automl_settings.n_cross_validations or
            (cv_splits_indices is not None) or automl_settings.validation_size):
        raise DataException(
            "No form of validation was provided. Please specify the data "
            "or type of validation you would like to use.")

    # validate sample weights if not None
    if sample_weight is not None:
        check_sample_weight(X, sample_weight, "X",
                            "sample_weight", automl_settings)

    if X_valid is not None and y_valid is None:
        raise DataException(
            "X validation provided but y validation data is missing.")

    if y_valid is not None and X_valid is None:
        raise DataException(
            "y validation provided but X validation data is missing.")

    if X_valid is not None and sample_weight is not None and \
            sample_weight_valid is None:
        raise DataException("sample_weight_valid should be set to a valid value")

    if sample_weight_valid is not None and X_valid is None:
        raise DataException(
            "sample_weight_valid should only be set if X_valid is set")

    if sample_weight_valid is not None:
        check_sample_weight(X_valid, sample_weight_valid,
                            "X_valid", "sample_weight_valid", automl_settings)

    utilities._check_dimensions(
        X=X, y=y, X_valid=X_valid, y_valid=y_valid,
        sample_weight=sample_weight, sample_weight_valid=sample_weight_valid)

    if X_valid is not None:
        if automl_settings.n_cross_validations is not None and \
                automl_settings.n_cross_validations > 0:
            raise DataException("Both custom validation data and "
                                "n_cross_validations specified. "
                                "If you are providing the training "
                                "data, do not pass any n_cross_validations.")
        if automl_settings.validation_size is not None and \
                automl_settings.validation_size > 0.0:
            raise DataException("Both custom validation data and "
                                "validation_size specified. If you are "
                                "providing the training data, do not pass "
                                "any validation_size.")

    if cv_splits_indices is not None:
        if automl_settings.n_cross_validations is not None and \
                automl_settings.n_cross_validations > 0:
            raise DataException("Both cv_splits_indices and n_cross_validations "
                                "specified. If you are providing the indices to "
                                "use to split your data. Do not pass any "
                                "n_cross_validations.")
        if automl_settings.validation_size is not None and \
                automl_settings.validation_size > 0.0:
            raise DataException("Both cv_splits_indices and validation_size "
                                "specified. If you are providing the indices to "
                                "use to split your data. Do not pass any "
                                "validation_size.")
        if X_valid is not None:
            raise DataException("Both cv_splits_indices and custom split "
                                "validation data specified. If you are providing "
                                "the training data, do not pass any indices to "
                                "split your data.")

    if automl_settings.n_cross_validations is not None:
        if y.shape[0] < automl_settings.n_cross_validations:
            raise ConfigException("Number of training rows ({}) is less than total requested CV splits ({}). "
                                  "Please reduce the number of splits requested."
                                  .format(y.shape[0], automl_settings.n_cross_validations))

    metrics_checks(X, y, automl_settings, X_valid, y_valid)


def incremental_learning_validate_and_subsample_inputs(
    X: DataInputType,
    y: DataInputType,
    X_valid: Optional[DataInputType],
    y_valid: Optional[DataInputType],
    sample_weight: Optional[DataInputType],
    sample_weight_valid: Optional[DataInputType]
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    If using incremental learning, validate and subsample data inputs.
    Subsampling the input Dataflows to numpy arrays this allows the validation flow (which
    can handle numpy arrays but not Dataflows directly at the moment) to proceed.

    :param X:
    :param y:
    :param X_valid:
    :param y_valid:
    :param sample_weight:
    :param sample_weight_valid:
    """

    input_must_be_dataflow_warning = "If using incremental learning, {} needs to be an Azure ML Dataflow"

    # check that all inputs are Dataflows
    if not isinstance(X, dprep.Dataflow):
        raise DataException(input_must_be_dataflow_warning.format('X'))
    if not isinstance(y, dprep.Dataflow):
        raise DataException(input_must_be_dataflow_warning.format('y'))
    if X_valid is not None and not isinstance(X_valid, dprep.Dataflow):
        raise DataException(input_must_be_dataflow_warning.format('X_valid'))
    if y_valid is not None and not isinstance(y_valid, dprep.Dataflow):
        raise DataException(input_must_be_dataflow_warning.format('y_valid'))
    if sample_weight is not None and not isinstance(sample_weight, dprep.Dataflow):
        raise DataException(input_must_be_dataflow_warning.format('sample_weight'))
    if sample_weight_valid is not None and not isinstance(sample_weight_valid, dprep.Dataflow):
        raise DataException(input_must_be_dataflow_warning.format('sample_weight_valid'))

    # validate that y is only a single column
    y_column_count = len(y.head(1).columns)
    if y_column_count != 1:
        raise DataException('y must contain only a single column, but {} columns were found'.format(y_column_count))

    # validate that column names are unique between X and y
    # (this is required, b/c we append the columns of X and y together to get a single merged Dataflow
    # that nimbus learners require as input. if X and y have shared column names, this merge throws an error)
    X_column_names = X.head(1).columns.tolist()
    y_column_name = y.head(1).columns[0]
    if y_column_name in X_column_names:
        raise DataException('The label column name {} was found in X. Please rename this column in X'
                            .format(y_column_name))

    # generate subsampled numpy arrays
    X = X.head(LargeDatasetLimit.MAX_ROWS_TO_SUBSAMPLE).values
    y = y.head(LargeDatasetLimit.MAX_ROWS_TO_SUBSAMPLE).iloc[:, 0].values
    if X_valid is not None:
        X_valid = X_valid.head(LargeDatasetLimit.MAX_ROWS_TO_SUBSAMPLE).values
    if y_valid is not None:
        y_valid = y_valid.head(LargeDatasetLimit.MAX_ROWS_TO_SUBSAMPLE).iloc[:, 0].values
    if sample_weight is not None:
        sample_weight = sample_weight.head(LargeDatasetLimit.MAX_ROWS_TO_SUBSAMPLE).iloc[:, 0].values
    if sample_weight_valid is not None:
        sample_weight_valid = sample_weight_valid.head(LargeDatasetLimit.MAX_ROWS_TO_SUBSAMPLE).iloc[:, 0].values

    return X, y, X_valid, y_valid, sample_weight, sample_weight_valid


def validate_training_data_dict(data_dict, automl_settings, check_sparse=False):
    """
    Validate that training data and parameters have been correctly provided.

    :param data_dict:
    :param automl_settings:
    :param check_sparse:
    :return:
    """
    X = data_dict.get('X', None)
    y = data_dict.get('y', None)
    sample_weight = data_dict.get('sample_weight', None)
    X_valid = data_dict.get('X_valid', None)
    y_valid = data_dict.get('y_valid', None)
    sample_weight_valid = data_dict.get('sample_weight_valid', None)
    cv_splits_indices = data_dict.get('cv_splits_indices', None)
    x_raw_column_names = data_dict.get('x_raw_column_names', None)
    validate_training_data(X, y, X_valid, y_valid, sample_weight, sample_weight_valid, cv_splits_indices,
                           automl_settings, check_sparse=check_sparse)
    if automl_settings.is_timeseries:
        validate_timeseries_training_data(automl_settings, X, y, X_valid, y_valid,
                                          sample_weight, sample_weight_valid, cv_splits_indices,
                                          x_raw_column_names)


def metrics_checks(x: DataInputType,
                   y: DataInputType,
                   automl_settings: AutoMLBaseSettings,
                   x_valid: Optional[DataInputType] = None,
                   y_valid: Optional[DataInputType] = None) -> None:
    """
    Validate input data for metrics.

    :param x: input data. dataframe/ array/ sparse matrix
    :param y: input labels. dataframe/series/array
    :param automl_settings: automl settings
    :raise: DataException if data is not suitable for metrics calculations
    :return:
    """
    if y_valid is not None:
        if automl_settings.task_type == constants.Tasks.CLASSIFICATION:
            primary_metric = automl_settings.primary_metric
            if primary_metric == constants.Metric.AUCWeighted:
                in_valid = set(y_valid[~pd.isnull(y_valid)])
                if len(in_valid) == 1:
                    remaining_metrics = utilities.get_primary_metrics(constants.Tasks.CLASSIFICATION).copy()
                    remaining_metrics.remove(primary_metric)
                    raise DataException(
                        "y_valid is single valued. "
                        "Please make sure that y_valid is well represented with all classes "
                        "for classification task. Or please try one of {} as primary metrics".format(
                            remaining_metrics))


def check_x_y(x: DataInputType,
              y: DataInputType,
              automl_settings: AutoMLBaseSettings,
              x_valid: Optional[DataInputType] = None,
              y_valid: Optional[DataInputType] = None,
              check_sparse: bool = False,
              logger: Optional[logging.Logger] = None) -> None:
    """
    Validate input data.

    :param x: input data. dataframe/ array/ sparse matrix
    :param y: input labels. dataframe/series/array
    :param automl_settings: automl settings
    :raise: DataException if data does not conform to accepted types and shapes
    :return:
    """

    if logger is not None:
        logger.info('Checking X and y.')

    is_timeseries = automl_settings.is_timeseries

    if x is None:
        raise DataException("X should not be None")

    if y is None:
        raise DataException("y should not be None")

    is_preprocess_enabled = automl_settings.preprocess is True or automl_settings.preprocess == "True"

    # If text data is not being preprocessed or featurized, then raise an error
    if not is_preprocess_enabled and not is_timeseries:
        without_preprocess_error_str = \
            "The training data contains {}, {} or {} data. Please set preprocess flag as True".format(
                _engineered_feature_names.FeatureTypeRecognizer.DateTime.lower(),
                _engineered_feature_names.FeatureTypeRecognizer.Categorical.lower(),
                _engineered_feature_names.FeatureTypeRecognizer.Text.lower())

        if isinstance(x, pd.DataFrame):
            for column in x.columns:
                if not utilities._check_if_column_data_type_is_numerical(
                        utilities._get_column_data_type_as_str(x[column].values)):
                    raise DataException(without_preprocess_error_str)
        elif isinstance(x, np.ndarray):
            if len(x.shape) == 1:
                if not utilities._check_if_column_data_type_is_numerical(
                        utilities._get_column_data_type_as_str(x)):
                    raise DataException(without_preprocess_error_str)
            else:
                for index in range(x.shape[1]):
                    if not utilities._check_if_column_data_type_is_numerical(
                            utilities._get_column_data_type_as_str(x[:, index])):
                        raise DataException(without_preprocess_error_str)

    if not ((is_preprocess_enabled and isinstance(x, pd.DataFrame)) or
            isinstance(x, np.ndarray) or scipy.sparse.issparse(x)):
        raise DataException(
            "x should be dataframe with preprocess set or numpy array"
            " or sparse matrix")

    if (check_sparse and scipy.sparse.issparse(x) and
        (automl_settings.enable_onnx_compatible_models is True or
         automl_settings.enable_onnx_compatible_models == "True")):
        raise DataException(
            "x should not be a sparse matrix when enable_onnx_compatible_models is True."
            "ONNX currently does not support sparse data.")

    if not isinstance(y, np.ndarray):
        raise DataException("y should be numpy array")

    if len(y.shape) > 2 or (len(y.shape) == 2 and y.shape[1] != 1):
        raise DataException("y should be a vector Nx1")

    if y is not None:
        if len(utilities._get_indices_missing_labels_output_column(y)) == y.shape[0]:
            raise DataException("y has all missing labels")

    if y_valid is not None:
        if len(utilities._get_indices_missing_labels_output_column(y_valid)) == y_valid.shape[0]:
            raise DataException("y_valid has all missing labels")

    if automl_settings.task_type == constants.Tasks.REGRESSION:
        if not utilities._check_if_column_data_type_is_numerical(
                utilities._get_column_data_type_as_str(y)):
            raise DataException(
                "Please make sure y is numerical before fitting for "
                "regression")

    if automl_settings.task_type == constants.Tasks.CLASSIFICATION:
        y_ravel = y.ravel()
        unique_classes = pd.Series(y_ravel).unique().shape[0]
        if unique_classes < 2:
            raise DataException(
                "For a classification task, the y input need at least two classes of labels."
            )

    # not check x Nan for preprocess enabled.
    check_x_nan = not is_preprocess_enabled
    # not check NaN in y data as we will automatically remove these data in the data_transformation.py.
    check_y_nan = False
    # always check x contains inf or not.
    check_x_inf = True
    # check y contains inf data raise errors and only in regression.
    check_y_inf = automl_settings.task_type != constants.Tasks.CLASSIFICATION
    _check_data_nan_inf(
        x, input_data_name="X", check_nan=check_x_nan, check_inf=check_x_inf)
    _check_data_nan_inf(y, input_data_name="y", check_nan=check_y_nan, check_inf=check_y_inf)
    _check_data_minimal_size(x, x_valid, automl_settings)
    if x_valid is not None:
        _check_data_nan_inf(
            x_valid, input_data_name="X_valid", check_nan=check_x_nan, check_inf=check_x_inf)
    if y_valid is not None:
        _check_data_nan_inf(
            y_valid, input_data_name="y_valid", check_nan=check_y_nan, check_inf=check_y_inf)


def _check_data_minimal_size(X: DataInputType, X_valid: DataInputType, automl_settings: AutoMLBaseSettings) -> None:
    """Check if the data is larger than minimum size."""

    # The rule is for train-valid minimal=2, and for cv, minimum=number of cv.
    if automl_settings.n_cross_validations is None:
        minimal_size = SmallDataSetLimit.TRAIN_VALID_MINIMAL_SIZE
    else:
        minimal_size = automl_settings.n_cross_validations
    if X.shape[0] < minimal_size:
        raise DataException(
            "The input data X is less than the minimum requirement size. "
            "Please add more data to avoid future exceptions."
        )
    if X_valid is not None and X_valid.shape[0] < minimal_size:
        raise DataException(
            "The input data X_valid is less than the minimum requirement size. "
            "Please add more data to avoid future exceptions."
        )
    if X.shape[0] < SmallDataSetLimit.WARNING_SIZE:
        warnings.warn(
            "The input data X has {} data points which is less than the recommended "
            "minimum data size {}. Please consider adding more data points to ensure better model accuracy.".
            format(X.shape[0], SmallDataSetLimit.WARNING_SIZE)
        )


def _check_data_nan_inf(data: DataInputType,
                        input_data_name: str,
                        check_nan: bool,
                        check_inf: bool = True) -> None:
    """Check if data contains nan or inf. If contains NaN, give out warning. If contains inf, raise exception."""
    if isinstance(data, pd.DataFrame):
        data_type = data.dtypes.dtype
    else:
        data_type = data.dtype
    is_integer_data = data_type.char in np.typecodes['AllInteger']
    n_top_indices = 20
    try:
        # The sklearn validation can be found here. If a dataset failed sklearn validation, it cannot be trained
        # by most of our pipeline.
        # https://github.com/scikit-learn/scikit-learn/blob/0.19.X/sklearn/utils/validation.py
        sk_validation.assert_all_finite(data)
        if check_nan and is_integer_data:
            # if the data is all integer, we will have a nan check beyond what sklearn does.
            input_data = data.data if scipy.sparse.issparse(data) else data
            if any(np.isnan(input_data)):
                raise ValueError
    except ValueError:
        # looking for nan and inf for the data. If the data contains other type, it will used in other checks.
        if data_type.char in np.typecodes['AllFloat'] or (check_nan and is_integer_data):
            if check_nan:
                nan_indices = _get_data_indices_by_mask_function(data, np.isnan)
                if nan_indices.shape[0] > 0:
                    print(
                        "WARNING: The following coordinates{} [{}] contains {} NaN(np.NaN) data in {}. "
                        "Please consider dropping these rows.".
                        format(_construct_coord_indices_str(nan_indices, n_top_indices),
                               "" if nan_indices.shape[0] < n_top_indices else "(first detected in each column)",
                               nan_indices.shape[0],
                               input_data_name)
                    )
            if check_inf:
                inf_indices = _get_data_indices_by_mask_function(data, np.isinf)
                if inf_indices.shape[0] > 0:
                    raise DataException(
                        "The following coordinates{} [{}] contains {} infinity(np.inf) data in {}. "
                        "Please consider dropping these rows.".
                        format(_construct_coord_indices_str(inf_indices, n_top_indices),
                               "" if inf_indices.shape[0] < n_top_indices else "(first detected in each column)",
                               inf_indices.shape[0],
                               input_data_name)
                    )


def _construct_coord_indices_str(data_indices: np.ndarray, n_top_indices: int = 20) -> str:
    """Contruct a string with top 20 indices."""
    if data_indices.ndim == 1 or data_indices.shape[1] == 1:
        indices = sorted(data_indices)
    else:
        indices = sorted(data_indices, key=lambda x: (x[1], x[0]))
    if len(indices) <= n_top_indices:
        print_indices = data_indices
        return ", ".join([str(idx) for idx in print_indices])
    else:
        if data_indices.ndim == 1:
            print_indices = data_indices[:n_top_indices]
        else:
            col_idx_dict = {}  # type: Dict[int, List[np.ndarray]]
            for idx in indices:
                if idx[1] not in col_idx_dict:
                    col_idx_dict[idx[1]] = [idx]
                else:
                    col_idx_dict[idx[1]].append(idx)
            top_indices = sorted(col_idx_dict.keys(), key=lambda x: len(col_idx_dict[x]))
            if len(top_indices) > n_top_indices:
                print_indices = [col_idx_dict[idx][0] for idx in top_indices[:n_top_indices]]
            else:
                print_indices = [col_idx_dict[idx][0] for idx in top_indices]
        return ", ".join([str(idx) for idx in print_indices]) + "..."


def _get_data_indices_by_mask_function(data: DataInputType,
                                       mask_function: 'Callable[..., Optional[Any]]') -> np.ndarray:
    """Obtain the indices list where the data entry in data has the mask function evaluated as True."""
    if isinstance(data, np.ndarray) or isinstance(data, pd.DataFrame):
        return np.argwhere(mask_function(data))
    elif scipy.sparse.issparse(data):
        coo_data = scipy.sparse.coo_matrix(data)
        return np.array([(coo_data.row[i], coo_data.col[i]) for i in np.argwhere(mask_function(coo_data.data))])


def check_sample_weight(x: DataInputType,
                        sample_weight: np.ndarray,
                        x_name: str,
                        sample_weight_name: str,
                        automl_settings: AutoMLBaseSettings) -> None:
    """
    Validate sample_weight.

    :param x:
    :param sample_weight:
    :param x_name:
    :param sample_weight_name:
    :param automl_settings:
    :raise DataException if sample_weight has problems
    :return:
    """
    if not isinstance(sample_weight, np.ndarray):
        raise DataException(sample_weight_name + " should be numpy array")

    if x.shape[0] != len(sample_weight):
        raise DataException(sample_weight_name +
                            " length should match length of " + x_name)

    if len(sample_weight.shape) > 1:
        raise DataException(sample_weight_name +
                            " should be a unidimensional vector")

    if automl_settings.primary_metric in \
            constants.Metric.SAMPLE_WEIGHTS_UNSUPPORTED_SET:
        raise DataException("Sample weights is not supported for these primary metrics: {0}"
                            .format(constants.Metric.SAMPLE_WEIGHTS_UNSUPPORTED_SET))


def validate_timeseries_training_data(automl_settings: AutoMLBaseSettings,
                                      X: DataInputType,
                                      y: DataInputType,
                                      X_valid: Optional[DataInputType] = None,
                                      y_valid: Optional[DataInputType] = None,
                                      sample_weight: Optional[np.ndarray] = None,
                                      sample_weight_valid: Optional[np.ndarray] = None,
                                      cv_splits_indices: Optional[np.ndarray] = None,
                                      x_raw_column_names: Optional[np.ndarray] = None) -> None:
    """
    Quick check of the timeseries input values, no tsdf is required here.

    :param X: Training data.
    :type X: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param automl_settings: automl settings
    """
    grain_set = set(automl_settings.grain_column_names) if isinstance(
        automl_settings.grain_column_names, list) else set([automl_settings.grain_column_names])
    if automl_settings.drop_column_names is not None:
        drop_set = set(automl_settings.drop_column_names) if isinstance(
            automl_settings.drop_column_names, list) else set([automl_settings.drop_column_names])
        if (automl_settings.time_column_name in drop_set):
            raise ConfigException("Time column cannot be dropped. Please remove it from the drop column list.")
            # Check if grain columns are overlapped with drop columns.
        if automl_settings.grain_column_names is not None:
            if drop_set.intersection(grain_set):
                raise ConfigException("Grain column cannot be dropped. Please remove it from the drop column list.")
    if automl_settings.time_column_name in grain_set:
        raise ConfigException("Time column name is present in the grain columns. Please remove it from grain list.")

    if automl_settings.n_cross_validations is None and X_valid is None:
        raise ConfigException("Timeseries only support cross validations and train validation splits.")
    elif cv_splits_indices is not None or \
            (automl_settings.validation_size is not None and automl_settings.validation_size > 0.0):
        if cv_splits_indices is not None:
            error_validation_config = "cv_splits_indices"
        else:
            error_validation_config = "validation_size"
        raise ConfigException(
            "Timeseries only support cross validation without any other combinations. "
            "But SDK found {} is passed in.".format(error_validation_config)
        )
    else:
        # quick check of the data, no need of tsdf here.
        window_size = automl_settings.window_size if automl_settings.window_size is not None else 0
        lags = automl_settings.lags[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN] \
            if automl_settings.lags is not None else [0]  # type: List[int]
        min_points = utilities.get_min_points(
            window_size,
            lags,
            automl_settings.max_horizon,
            automl_settings.n_cross_validations)
        if X.shape[0] < min_points:
            print(
                "The data points should have at least {} for a valid training with cv {}, max_horizon {}, lags {} "
                "and rolling window size {}. The current dataset has only {} points. Please consider reducing your "
                "horizon, the number of cross validations, lags or rolling window size."
                .format(
                    min_points, automl_settings.n_cross_validations, automl_settings.max_horizon,
                    lags, window_size, X.shape[0]
                )
            )
            raise DataException("The data provided is insufficient for training.")

        tsdf = _check_timeseries_input_and_get_tsdf(
            X, y, x_raw_column_names, automl_settings, min_points, is_validation_data=False)
        tsdf_valid = None
        if X_valid is not None:
            tsdf_valid = _check_timeseries_input_and_get_tsdf(
                X_valid, y_valid, x_raw_column_names, automl_settings, min_points=0, is_validation_data=True)
            _validate_timeseries_train_valid_tsdf(tsdf, tsdf_valid, bool(window_size + max(lags)))


def _check_tsdf_frequencies(frequencies_grain_names: Dict[pd.DateOffset, List[List[str]]]) -> None:
    # pd.DateOffset can not compare directly. need a start time.
    if len(frequencies_grain_names) == 0:
        return
    date_offsets = [offset for offset in frequencies_grain_names.keys()]
    all_freq_equal = all([offset == date_offsets[0] for offset in date_offsets])
    if not all_freq_equal:
        msg = ("More than one series is in the input data, and their frequencies differ. "
               "Please separate series by frequency and build separate models. "
               "If frequencies were incorrectly inferred, please fill in gaps in series.")
        raise DataException(msg)


def _check_grain_min_points(data_points: int,
                            min_points: int,
                            automl_settings: AutoMLBaseSettings,
                            grain_names: Optional[Union[List[str], str]] = None) -> None:
    if hasattr(
            automl_settings,
            TimeSeries.SHORT_SERIES_HANDLING) and getattr(
            automl_settings,
            TimeSeries.SHORT_SERIES_HANDLING):
        # If we are going to remove short series, do not validate for it.
        # If all series are too short, grain dropper will throw an error.
        return
    if data_points < min_points:
        window_size = automl_settings.window_size if automl_settings.window_size is not None else 0
        lags = automl_settings.lags[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN] \
            if automl_settings.lags is not None else 0
        if grain_names is None:
            print("The data provided is insufficient for training: for a valid training with cv {},  max_horizon {}, "
                  "lags {} and rolling window size {}. The current dataset has only {} points. Please consider "
                  "reducing max_horizon, the number of cross validations, lags or rolling window size.".
                  format(automl_settings.n_cross_validations,
                         automl_settings.max_horizon, lags, window_size, data_points))
            raise DataException("The data provided is insufficient for training.")
        else:
            if not isinstance(grain_names, list):
                grain_names = [grain_names]
            print("The data provided is insufficient for training grain: [{}] for a valid training with cv {}, "
                  "max_horizon {} lags {} and rolling window size {}. The current grain has only {} points. "
                  "Please consider reducing max_horizon, n_cross_validations, or lags, rolling window size or "
                  "dropping that particular grain.".
                  format(",".join([str(grain) for grain in grain_names]),
                         automl_settings.n_cross_validations,
                         automl_settings.max_horizon, lags, window_size, data_points))
            raise DataException("The data provided is insufficient for some training grains.")


def _check_timeseries_input_and_get_tsdf(
    X: DataInputType,
    y: DataInputType,
    x_raw_column_names: np.ndarray,
    automl_settings: AutoMLBaseSettings,
    min_points: int = 0,
    is_validation_data: bool = False
) -> TimeSeriesDataFrame:
    if isinstance(X, pd.DataFrame):
        df = X
    else:
        if x_raw_column_names is not None:
            # check if there is any conflict in the x_raw_column_names
            _check_timeseries_input_column_names(x_raw_column_names)
            # generate dataframe for tsdf.
            df = _add_raw_column_names_to_X(x_raw_column_names, X)
        else:
            # if x_raw_column_name is None, then the origin input data is ndarray.
            raise DataException(
                "Timeseries only support pandas DataFrame as input X. The raw input X is {}.".format(
                    "sparse" if scipy.sparse.issparse(X) else "ndarray"
                )
            )
    timeseries_param_dict = utilities._get_ts_params_dict(automl_settings)
    _check_columns_present(df, cast(Dict[str, str], timeseries_param_dict))
    # Check not supported datatypes and warn
    _check_supported_data_type(df)
    if timeseries_param_dict is not None:
        tst = TimeSeriesTransformer(pipeline_type=TimeSeriesPipelineType.FULL,
                                    logger=None, **timeseries_param_dict)
    else:
        raise ConfigException("Invalid forecasting parameters were provided.")
    _check_time_index_duplication(df, automl_settings.time_column_name, automl_settings.grain_column_names)
    _check_valid_pd_time(df, automl_settings.time_column_name)
    tsdf = tst.construct_tsdf(df, y)
    _check_timeseries_imputation(tsdf.copy())
    tsdf.sort_index(inplace=True)
    frequencies_grain_names = {}   # type: Dict[pd.DateOffset, List[List[str]]]
    if automl_settings.grain_column_names is not None:
        # to deal the problem that user has no input grain
        for data_tuple in tsdf.groupby_grain():
            grain_name_str = data_tuple[0]
            err_msg = ("Time series frequency cannot be inferred for grain (series) [{}]. "
                       "Please ensure that each time series' time stamps are regularly spaced. "
                       "Filling with default values such as 0 may be needed for very sparse series."
                       ).format(grain_name_str)
            try:
                tsdf_grain = data_tuple[1]
                data_points = tsdf_grain.shape[0]
                if not is_validation_data or tsdf_grain.shape[0] > 1:
                    # if validation data is only one data point, no need to check freq.
                    freq = tsdf_grain.infer_freq()
                    if freq is None:
                        print(err_msg)
                        raise DataException("Frequency cannot be inferred for the [masked] grain.")
                    if freq in frequencies_grain_names:
                        frequencies_grain_names[freq].append(grain_name_str)
                    else:
                        frequencies_grain_names[freq] = [grain_name_str]
                    # check min data points for train and max_horizon for validation
                    data_points = len(
                        pd.date_range(
                            start=tsdf_grain.time_index.min(),
                            end=tsdf_grain.time_index.max(),
                            freq=tsdf_grain.infer_freq()))
                    if not is_validation_data:
                        _check_grain_min_points(
                            data_points, min_points, automl_settings, grain_names=grain_name_str)
                if is_validation_data:
                    if data_points < automl_settings.max_horizon:
                        print("WARNING: Validation set has fewer data points ({}) "
                              "than max_horizon ({}) for grain (series) [{}]. "
                              "We will be unable to estimate error and predictive quantiles at some horizons. "
                              "Please consider increasing the validation data to the length of max horizon.".
                              format(data_points, automl_settings.max_horizon, grain_name_str))
                    elif data_points > automl_settings.max_horizon:
                        print(("WARNING: Validation set has more data points {} "
                               "than max_horizon {} for grain (series) [{}]. "
                               "Not all validation data will be used in the training. "
                               "Please consider decreasing the validation data to the length of max horizon.").
                              format(data_points, automl_settings.max_horizon, grain_name_str))
            except DataException:
                # If we already have a descriptive Exception, raise it.
                raise
            except Exception:
                # If not, raise generic exception.
                raise DataException("A non-specific error occurred checking frequencies across grains (series).")

        _check_tsdf_frequencies(frequencies_grain_names)
    # check all the tsdf at the end.
    if not is_validation_data:
        data_points = len(pd.date_range(
            start=tsdf.time_index.min(), end=tsdf.time_index.max(), freq=tsdf.infer_freq()))
        _check_grain_min_points(data_points, min_points, automl_settings)
    return tsdf


def _check_valid_pd_time(df: pd.DataFrame, time_column_name: str) -> None:
    try:
        pd.to_datetime(df[time_column_name])
    except pd.tslib.OutOfBoundsDatetime:
        raise DataException("Date/time is out of our usable range. "
                            "Please drop any rows with date/time less than {} or greater than {}."
                            .format(pd.Timestamp.min, pd.Timestamp.max))
    except ValueError:
        raise DataException("One or more rows have an invalid date/time. "
                            "Please ensure you can run `pandas.to_datetime(X)`.")


def _check_time_index_duplication(df: pd.DataFrame,
                                  time_column_name: str,
                                  grain_column_names: Optional[List[str]] = None) -> None:
    group_by_col = [time_column_name]
    if grain_column_names is not None:
        if isinstance(grain_column_names, str):
            grain_column_names = [grain_column_names]
        group_by_col.extend(grain_column_names)
    duplicateRowsDF = df[df.duplicated(subset=group_by_col, keep=False)]
    if duplicateRowsDF.shape[0] > 0:
        if grain_column_names is not None and len(grain_column_names) > 0:
            message = ("Found duplicated rows for {} and {} combinations. "
                       "Please make sure the grain setting is correct so that each grain represents "
                       "one time-series, or clean the data to make sure there are no duplicates "
                       "before passing to AutoML. One duplicated example: ".
                       format([time_column_name], grain_column_names))
            print(message)
            print(duplicateRowsDF.iloc[:2, :][group_by_col])
            raise DataException("Duplicates in time and grain combinations.")
        else:
            message = ("Found duplicated rows for timeindex column {}. "
                       "Please clean the data to make sure there are no duplicates "
                       "before passing to AutoML. One duplicated example: ".
                       format([time_column_name]))
            print(message)
            print(duplicateRowsDF.iloc[:2, :][group_by_col])
            raise DataException("Duplicates in time index.")


def _check_timeseries_imputation(tsdf: TimeSeriesDataFrame) -> None:
    """
    Check if imputation can be applied to the tsdf.

    :param tsdf: The time series dataframe to be tested.
    """
    try:
        for grain, tsdf_one in tsdf.groupby_grain():
            if tsdf_one.shape[0] > 1:
                # We do not need to check imputation on data
                # frame with only one time point.
                tsdf_one.fill_datetime_gap()
    except DataFrameFrequencyException:
        # If the error related to inability of
        # imputation for one grain.
        raise DataException('The dates in one of the grains are not regular '
                            'and data frequency can not be established. '
                            'Please check dates and remove the irregular grain.')
    except DataFrameValueException:
        # In AutoML setting this exception never happens.
        raise DataException('The time column in dataframe has incorrect type. '
                            'Please make sure it contains dates.')


def _validate_timeseries_train_valid_tsdf(tsdf_train: TimeSeriesDataFrame,
                                          tsdf_valid: TimeSeriesDataFrame,
                                          has_lookback_features: bool) -> None:
    train_grain_data_dict = {grain: tsdf for grain, tsdf in tsdf_train.groupby_grain()}
    valid_grain_data_dict = {grain: tsdf for grain, tsdf in tsdf_valid.groupby_grain()}
    train_grain = set([g for g in train_grain_data_dict.keys()])
    valid_grain = set([g for g in valid_grain_data_dict.keys()])
    # check grain is the same for train and valid.
    grain_difference = train_grain.symmetric_difference(valid_grain)
    if len(grain_difference) > 0:
        grain_in_train_not_in_valid = list(filter(lambda x: x in train_grain, grain_difference))
        grain_in_valid_not_in_train = list(filter(lambda x: x in valid_grain, grain_difference))
        error_msg_list = []
        if len(grain_in_train_not_in_valid) > 0:
            error_msg_list.append(
                "Grain {} found in training data but not in validation data.".format(
                    ",".join(["[{}]".format(grain) for grain in grain_in_train_not_in_valid])
                )
            )
        if len(grain_in_valid_not_in_train) > 0:
            error_msg_list.append(
                "Grain {} found in validation data but not in training data.".format(
                    ",".join(["[{}]".format(grain) for grain in grain_in_valid_not_in_train])
                )
            )
        print(" ".join(error_msg_list))
        raise DataException("Train and valid grain are not the same.")
    # check per grain contiguous and frequency.
    for grain, tsdf in train_grain_data_dict.items():
        tsdf_valid = valid_grain_data_dict[grain]
        if has_lookback_features and tsdf.time_index.max() + tsdf.infer_freq() != tsdf_valid.time_index.min():
            print("Training and validation data are not contiguous in grain(s) {}.".
                  format("[{}]".format(",".join([str(g) for g in grain]))))
            raise DataException(
                "Training and validation data are not contiguous in some grain(s)."
            )
        if tsdf_valid.shape[0] > 1:
            if tsdf.infer_freq() != tsdf_valid.infer_freq():
                print("For grain {}, training data and validation data have different frequency.".
                      format("[{}]".format(",".join([str(g) for g in grain]))))
                raise DataException(
                    "For some grains, training data and validation data have different frequency."
                )


def _check_timeseries_input_column_names(x_raw_column_names: np.ndarray) -> None:
    for col in x_raw_column_names:
        if col in constants.TimeSeriesInternal.RESERVED_COLUMN_NAMES:
            print("Column name {} is in the reserved column names list, please change that column name.".format(col))
            raise DataException(
                "Column name is in the reserved column names list, please change that column name."
            )


def _check_columns_present(df: pd.DataFrame, timeseries_param_dict: Dict[str, str]) -> None:
    """Determine if df has the correct column names for timeseries."""
    msg = ("One or more columns for `{}` were not found. Please check that these columns "
           "are present in your dataframe. You can run `<X>.columns`.")

    def check_a_in_b(a: Union[str, List[str]], b: List[str]) -> List[str]:
        """
        checks a is in b.

        returns any of a not in b.
        """
        if isinstance(a, str):
            a = [a]

        set_a = set(a)
        set_b = set(b)
        return list(set_a - set_b)

    missing_col_names = []          # type: List[str]
    # check time column in df
    col_name = timeseries_param_dict.get(constants.TimeSeries.TIME_COLUMN_NAME)
    if col_name is not None:
        missing_col_names = check_a_in_b(col_name, df.columns)
    # raise if missing
    if len(missing_col_names) != 0:
        raise DataException(msg.format(constants.TimeSeries.TIME_COLUMN_NAME))

    # check grain column(s) in df
    col_names = timeseries_param_dict.get(constants.TimeSeries.GRAIN_COLUMN_NAMES)
    if col_names is not None:
        missing_col_names = check_a_in_b(col_names, df.columns)
    # raise if missing
    if len(missing_col_names) != 0:
        raise DataException(msg.format(constants.TimeSeries.GRAIN_COLUMN_NAMES))

    # check drop column(s) in df
    missing_drop_cols = []         # type: List[str]
    col_names = timeseries_param_dict.get(constants.TimeSeries.DROP_COLUMN_NAMES)
    if col_names is not None:
        missing_drop_cols += check_a_in_b(col_names, df.columns)

    # warn if missing
    if len(missing_drop_cols) != 0:
        warnings.warn(
            "The following columns to drop were not found and will be ignored: {}.".format(missing_drop_cols)
        )


def _check_supported_data_type(df: pd.DataFrame) -> None:
    supported_datatype = set([np.number, np.dtype(object), pd.Categorical.dtype, np.datetime64])
    unknown_datatype = set(df.infer_objects().dtypes) - supported_datatype
    if(len(unknown_datatype) > 0):
        warnings.warn("Following datatypes: {} are not recognized".
                      format(unknown_datatype))


def _is_sparse_matrix_int_type(sparse_matrix: DataInputType) -> bool:
    """
    Check if a sparse matrix is in integer format.

    :param sparse_matrix:
    :return:
    """
    if sparse_matrix is not None and scipy.sparse.issparse(sparse_matrix):
        numpy_int_types = [np.int32, np.int64, np.int16, np.int8,
                           np.uint32, np.uint64, np.uint16, np.uint8]

        if sparse_matrix.dtype in numpy_int_types:
            return True

    return False


def _upgrade_sparse_matrix_type(sparse_matrix: DataInputType) -> DataInputType:
    """
    Convert sparse matrix in integer format into floating point format.

    This function will create a copy of the sparse matrix in when the conversion happens.
    :param sparse_matrix:
    :return:
    """
    if sparse_matrix is not None and scipy.sparse.issparse(sparse_matrix):
        if sparse_matrix.dtype == np.int32 or sparse_matrix.dtype == np.int16 or \
                sparse_matrix.dtype == np.int8 or sparse_matrix.dtype == np.uint32 or \
                sparse_matrix.dtype == np.uint16 or sparse_matrix.dtype == np.uint8:
            return sparse_matrix.astype(np.float32)
        elif sparse_matrix.dtype == np.int64 or sparse_matrix.dtype == np.uint64:
            return sparse_matrix.astype(np.float64)
        else:
            return sparse_matrix

    return sparse_matrix


def init_client_dataset_from_fit_iteration_params(fit_iteration_parameters_dict: Dict[str, Any],
                                                  automl_settings: AutoMLBaseSettings,
                                                  cache_store: Optional[CacheStore] = None,
                                                  remote: bool = False,
                                                  init_all_stats: bool = False,
                                                  keep_in_memory: bool = False) -> ClientDatasets:
    """
    Get a ClientDatasets object from fit_iteration_parameters

    TODO: This method needs to be deprecated. ClientDatasets should be consolidated to only use transformed data ctx

    :param fit_iteration_parameters_dict: Dictionary that contains input data
    :param automl_settings:  AutoML settings config
    :param cache_store: Underlying cache store to use, will default to local FileStore
    :param remote: remote or local run flag
    :param init_all_stats: Initialize all the stats
    :param keep_in_memory: Whether to flush the data to the cache store or keep it in-memory
    :return: ClientDatasets
    """
    cv_splits = _CVSplits(X=fit_iteration_parameters_dict.get('X'),
                          y=fit_iteration_parameters_dict.get('y'),
                          frac_valid=automl_settings.validation_size,
                          cv_splits_indices=fit_iteration_parameters_dict.get('cv_splits_indices'),
                          is_time_series=automl_settings.is_timeseries,
                          timeseries_param_dict=utilities._get_ts_params_dict(automl_settings))

    dataset = _get_client_dataset(fit_iteration_parameters_dict.get('X'),
                                  fit_iteration_parameters_dict.get('y'),
                                  cache_store=cache_store,
                                  sample_weight=fit_iteration_parameters_dict.get('sample_weight'),
                                  X_valid=fit_iteration_parameters_dict.get('X_valid'),
                                  y_valid=fit_iteration_parameters_dict.get('y_valid'),
                                  sample_weight_valid=fit_iteration_parameters_dict.get('sample_weight_valid'),
                                  cv_splits=cv_splits,
                                  num_classes=automl_settings.num_classes,
                                  task_type=automl_settings.task_type,
                                  y_min=automl_settings.y_min,
                                  y_max=automl_settings.y_max,
                                  init_all_stats=init_all_stats,
                                  remote=remote)

    dataset.x_raw_column_names = fit_iteration_parameters_dict.get('x_raw_column_names')

    if not keep_in_memory:
        dataset.cache_dataset(keep_in_memory)

    return dataset


def init_dataset(
    transformed_data_context: TransformedDataContext,
    cache_store: CacheStore,
    automl_settings: AutoMLBaseSettings,
    remote: bool = False,
    init_all_stats: bool = False,
    keep_in_memory: bool = False
) -> DatasetBase:
    """
    Initialize the dataset.

    :param transformed_data_context: transformed_data_context contains X,y & other data's.
    :param cache_store: cache store
    :param automl_settings: automl settings
    :param remote: remote or local run flag
    :param init_all_stats: init all stats
    :param keep_in_memory: Whether to flush the data to the cache store or keep it in-memory
    :return: DatasetBase
    """
    if automl_settings.use_incremental_learning:
        return init_streaming_dataset(
            transformed_data_context=transformed_data_context,
            automl_settings=automl_settings
        )

    return init_client_dataset(
        transformed_data_context=transformed_data_context,
        cache_store=cache_store,
        automl_settings=automl_settings,
        remote=remote,
        init_all_stats=init_all_stats,
        keep_in_memory=keep_in_memory)


def init_client_dataset(transformed_data_context: TransformedDataContext,
                        cache_store: CacheStore,
                        automl_settings: AutoMLBaseSettings,
                        remote: bool = False,
                        init_all_stats: bool = False,
                        keep_in_memory: bool = False) -> ClientDatasets:
    """
    Get the client dataset.

    :param transformed_data_context: transformed_data_context contains X,y & other data's.
    :param cache_store: cache store
    :param automl_settings: automl settings
    :param remote: remote or local run flag
    :param init_all_stats: init all stats
    :param keep_in_memory: Whether to flush the data to the cache store or keep it in-memory
    :return: ClientDatasets
    """
    dataset = _get_client_dataset(transformed_data_context.X,
                                  transformed_data_context.y,
                                  cache_store=cache_store,
                                  sample_weight=transformed_data_context.sample_weight,
                                  X_valid=transformed_data_context.X_valid,
                                  y_valid=transformed_data_context.y_valid,
                                  sample_weight_valid=transformed_data_context.sample_weight_valid,
                                  cv_splits=transformed_data_context.cv_splits,
                                  num_classes=automl_settings.num_classes,
                                  task_type=automl_settings.task_type,
                                  y_min=automl_settings.y_min,
                                  y_max=automl_settings.y_max,
                                  init_all_stats=init_all_stats,
                                  remote=remote,
                                  transformers=transformed_data_context.transformers)
    dataset.timeseries = transformed_data_context.timeseries
    dataset.timeseries_param_dict = transformed_data_context.timeseries_param_dict
    dataset.x_raw_column_names = transformed_data_context.x_raw_column_names
    dataset.raw_data_type = transformed_data_context._get_raw_data_type()
    dataset.raw_data_snapshot_str = transformed_data_context._get_raw_data_snapshot_str()

    if not keep_in_memory:
        dataset.cache_dataset(keep_in_memory)

    return dataset


def _get_client_dataset(X: DataInputType,
                        y: DataSingleColumnInputType,
                        cache_store: Optional[CacheStore] = None,
                        sample_weight: Optional[DataInputType] = None,
                        X_valid: Optional[DataInputType] = None,
                        y_valid: Optional[DataSingleColumnInputType] = None,
                        sample_weight_valid: Optional[DataInputType] = None,
                        cv_splits: Optional[_CVSplits] = None,
                        num_classes: Optional[int] = None,
                        task_type: str = constants.Tasks.CLASSIFICATION,
                        y_min: Optional[float] = None,
                        y_max: Optional[float] = None,
                        init_all_stats: bool = False,
                        remote: bool = True,
                        transformers: Optional[Dict[str, TransformerMixin]] = None) -> ClientDatasets:
    assert_failures = []
    default_dataset_name = 'NoName'

    if cv_splits:
        frac_valid = cv_splits.get_fraction_validation_size()
        cv_splits_indices = cv_splits.get_custom_split_indices()
        num_cv_folds = cv_splits.get_num_k_folds()
    else:
        frac_valid = None
        cv_splits_indices = None
        num_cv_folds = None

    subsample_cache_strategy = SubsampleCacheStrategy.Classic if remote \
        else SubsampleCacheStrategy.Preshuffle

    dataset = ClientDatasets(subsample_cache_strategy=subsample_cache_strategy, cache_store=cache_store)

    if X_valid is not None:
        training_type = _get_training_type(
            constants.TrainingType.TrainAndValidation)

        if not (num_cv_folds == 0 or num_cv_folds is None):
            assert_failures.append(
                'n_cross_validations cannot be specified when X_valid is provided.')

        if not (frac_valid == 0.0 or frac_valid is None):
            assert_failures.append(
                'validation_size cannot be specified when X_valid is provided.')

        if y_valid is None:
            assert_failures.append(
                'y_valid must also be provided when X_valid is provided.')

        if len(assert_failures) > 0:
            raise ConfigException("Bad fit parameters. Please review documentation for fit. " +
                                  ' '.join(assert_failures))
        dataset.parse_simple_train_validate(name=default_dataset_name,
                                            X=X,
                                            y=y,
                                            sample_weight=sample_weight,
                                            X_valid=X_valid,
                                            y_valid=y_valid,
                                            sample_weight_valid=sample_weight_valid,
                                            task=task_type,
                                            y_min=y_min,
                                            y_max=y_max,
                                            init_all_stats=init_all_stats,
                                            transformers=transformers)

    else:
        if (num_cv_folds == 0 or num_cv_folds is None) and cv_splits_indices is None:
            training_type = _get_training_type(
                constants.TrainingType.TrainAndValidation)
        else:
            if cv_splits_indices is not None:
                num_cv_folds = len(cv_splits_indices)
            training_type = _get_training_type(
                constants.TrainingType.MeanCrossValidation, num_cv_folds)

        if len(assert_failures) > 0:
            raise ConfigException("Bad fit parameters. Please review documentation for fit. " +
                                  ' '.join(assert_failures))

        dataset.parse_data(name=default_dataset_name,
                           X=X,
                           y=y,
                           sample_weight=sample_weight,
                           cv_splits=cv_splits,
                           num_classes=num_classes,
                           task=task_type,
                           y_min=y_min,
                           y_max=y_max,
                           init_all_stats=init_all_stats,
                           transformers=transformers)

    dataset.training_type = training_type

    return dataset


def init_streaming_dataset(
    transformed_data_context: TransformedDataContext,
    automl_settings: AutoMLBaseSettings
) -> StreamingDataset:
    """
    Initialize a streaming dataset (a dataset where where all data may not fit into memory at once).

    :param transformed_data_context: The transformed data context.
    :param automl_settings: AutoML settings
    :return: A StreamingDataset
    """

    return StreamingDataset(X=transformed_data_context.X,
                            y=transformed_data_context.y,
                            sample_weight=transformed_data_context.sample_weight,
                            X_valid=transformed_data_context.X_valid,
                            y_valid=transformed_data_context.y_valid,
                            sample_weight_valid=transformed_data_context.sample_weight_valid,
                            task=automl_settings.task_type)


def _get_training_type(training_type: str, folds: int = 0) -> str:
    """
    Determine what type of training and validation to do based on user inputs.
    """
    # TODO: make this simpler
    valid_training_types = (constants.TrainingType.TrainAndValidation,
                            constants.TrainingType.MeanCrossValidation)
    if training_type not in valid_training_types:
        raise ConfigException(
            "%s and %s are the only supported training types." % valid_training_types)
    is_cv = training_type == constants.TrainingType.MeanCrossValidation
    if not ((is_cv and folds) or (not is_cv and not folds)):
        raise ConfigException("Cannot specify number of folds "
                              "if training type is not %s" % constants.TrainingType.MeanCrossValidation)
    if folds < 0 or folds == 1:
        raise ConfigException(
            "Cross validation folds must be greater than 1, got %d" % folds)
    return training_type


def _extract_user_data(user_script: Any) -> Dict[str, Optional[Union[np.array, List[str], float, List[int]]]]:
    """
    Extract data from user's module containing get_data().

    This method automatically runs during an automated machine learning experiment.
    Arguments:
        user_script {module} -- Python module containing get_data() function.

    Raises:
        DataException -- Get data script was not defined and X, y inputs were not provided.
        DataException -- Could not execute get_data() from user script.
        DataException -- Could not extract data from user script.

    Returns:
        dict -- Dictionary containing
        X_train, y_train, sample_weight, X_valid, y_valid,
        sample_weight_valid, cv_splits_indices.

    """
    if user_script is None:
        raise DataException(
            "Get data script was not defined and X,"
            " y inputs were not provided.")
    try:
        output = user_script.get_data()         # type: Union[Dict[str, Any], Tuple[Any, Any, Any, Any]]
    except Exception as ex:
        raise DataException("Could not execute get_data() from user script."
                            "Exception: {}".format(ex)) from None
    if isinstance(output, dict):
        return _extract_data_from_dict(output)
    elif isinstance(output, tuple):
        return _extract_data_from_tuple(output)
    else:
        raise DataException("The output of get_data() from user script is not a dict or a tuple.")


def _extract_data_from_dict(output: Dict[str, Any]) -> \
        Dict[str, Optional[Union[np.array, List[str], float, List[int]]]]:
    """
    Extract user data if it is passed as a dictionary.

    Arguments:
        output {dict} -- dictionary containing user data and metadata.

    Raises:
        DataException -- Invalid data or encountered processing issues.

    Returns:
        dict -- Dictionary containing AutoML relevant data.

    """
    X = utilities.get_value_from_dict(output, ['X'], None)
    y = utilities.get_value_from_dict(output, ['y'], None)
    sample_weight = utilities.get_value_from_dict(output, ['sample_weight'], None)
    X_valid = utilities.get_value_from_dict(output, ['X_valid'], None)
    y_valid = utilities.get_value_from_dict(output, ['y_valid'], None)
    sample_weight_valid = utilities.get_value_from_dict(
        output, ['sample_weight_valid'], None)
    X_test = utilities.get_value_from_dict(output, ['X_test'], None)
    y_test = utilities.get_value_from_dict(output, ['y_test'], None)
    data = utilities.get_value_from_dict(output, ['data_train'], None)
    columns = utilities.get_value_from_dict(output, ['columns'], None)
    label = utilities.get_value_from_dict(output, ['label'], None)
    cv_splits_indices = utilities.get_value_from_dict(
        dictionary=output,
        names=["cv_splits_indices"], default_value=None)
    x_raw_column_names = None

    if data is not None:
        if label is None and X is None and y is None:
            raise DataException('Pandas data array received without a label. '
                                'Please add a ''label'' element to the '
                                'get_data() output.')
        if not isinstance(label, list):
            assert(isinstance(label, str) or isinstance(label, int))
            label = [label]
        y_extracted = data[label].values
        X_extracted = data[data.columns.difference(label)]
        if columns is not None:
            X_extracted = X_extracted[X_extracted.columns.intersection(
                columns)]

        if X is None and y is None:
            X = X_extracted
            y = y_extracted
        else:
            if np.array_equiv(X, X_extracted.values):
                raise DataException(
                    "Different values for X and data were provided. "
                    "Please return either X and y or data and label.")
            if np.array_equiv(y, y_extracted.values):
                raise DataException(
                    "Different values for y and label were provided. "
                    "Please return either X and y or data and label.")
    if isinstance(X, pd.DataFrame):
        x_raw_column_names = X.columns.values
        X = X.values
    if isinstance(X_valid, pd.DataFrame):
        X_valid = X_valid.values
    if isinstance(X_test, pd.DataFrame):
        X_test = X_test.values
    if isinstance(y, pd.DataFrame):
        y = y.values
    if isinstance(y_valid, pd.DataFrame):
        y_valid = y_valid.values
    if isinstance(y_test, pd.DataFrame):
        y_test = y_test.values

    if X is None:
        raise DataException(
            "Could not retrieve X train data from get_data() call. "
            "Please ensure you are either returning either "
            "{X_train: <numpy array>, y_train: <numpy array>"
            "or {data: <pandas dataframe>, label: <string>")
    if y is None:
        raise DataException(
            "Could not retrieve y train data from get_data() call. "
            "Please ensure you are either returning either "
            "{X_train: <numpy array>, y_train: <numpy array>"
            "or {data: <pandas dataframe>, label: <string>")

    if (X_valid is None) is not (y_valid is None):
        raise DataException(
            'Received only one of X_valid or y_valid.'
            'Either both or neither value should be provided.')

    return {
        "X": X,
        "y": y,
        "x_raw_column_names": x_raw_column_names,
        "sample_weight": sample_weight,
        "X_valid": X_valid,
        "y_valid": y_valid,
        "sample_weight_valid": sample_weight_valid,
        "X_test": X_test,
        "y_test": y_test,
        "cv_splits_indices": cv_splits_indices,
    }


def _extract_data_from_tuple(
        output: Tuple[Union[pd.DataFrame, np.array], Union[pd.DataFrame, np.array],
                      Union[pd.DataFrame, np.array], Union[pd.DataFrame, np.array]]) \
        -> Dict[str, Optional[Union[np.array, List[str], float, List[int]]]]:
    """
    Extract user data if it is passed as a tuple.

    Arguments:
        output {tuple} -- tuple containing user data.

    Raises:
        DataException -- Could not extract X, y from get_data() in user script. get_data only output {0} values.

    Returns:
        tuple -- tuple containing X_train, y_train, X_test, y_test

    """
    X_valid, y_valid = None, None
    if len(output) < 2:
        raise DataException("Could not extract X, y from get_data() in user "
                            "script. get_data only output {0} values."
                            .format(len(output))) from None
    x_raw_column_names = None
    X = output[0]
    y = output[1]
    if isinstance(X, pd.DataFrame):
        x_raw_column_names = X.columns.values
        X = X.values
    if isinstance(y, pd.DataFrame):
        y = y.values

    if len(output) >= 4:
        X_valid = output[2]
        y_valid = output[3]
        if isinstance(y_valid, pd.DataFrame):
            y_valid = y_valid.values
        if isinstance(X_valid, pd.DataFrame):
            X_valid = X_valid.values

    return {
        "X": X,
        "y": y,
        "sample_weight": None,
        "x_raw_column_names": x_raw_column_names,
        "X_valid": X_valid,
        "y_valid": y_valid,
        "sample_weight_valid": None,
        "X_test": None,
        "y_test": None,
        "cv_splits_indices": None,
    }
