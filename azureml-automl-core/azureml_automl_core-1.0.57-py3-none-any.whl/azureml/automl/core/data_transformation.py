# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Holding the preprocess functions."""
import logging
from typing import Optional, Any, Tuple

import numpy as np
import pandas as pd
import scipy
from sklearn import preprocessing

from automl.client.core.common import constants, utilities, memory_utilities
from automl.client.core.common._cv_splits import _CVSplits, FeaturizedCVSplit, FeaturizedTrainValidTestSplit
from automl.client.core.common.cache_store import CacheStore
from automl.client.core.common.exceptions import DataException, RawDataSnapshotException
from automl.client.core.common.forecasting_exception import AzureMLForecastException
from automl.client.core.common.types import DataInputType
from ._experiment_observer import ExperimentStatus, ExperimentObserver, NullExperimentObserver
from .data_context import RawDataContext, TransformedDataContext
from .faults_verifier import VerifierManager
from .featurization import DataTransformer
from .featurization import StreamingFeaturizer
from .featurizer.transformer import LaggingTransformer, TimeSeriesPipelineType, TimeSeriesTransformer
from .stats_computation import RawFeatureStats


def transform_data(raw_data_context: RawDataContext,
                   preprocess: bool = False,
                   cache_store: Optional[CacheStore] = None,
                   is_onnx_compatible: bool = False,
                   logger: Optional[logging.Logger] = None,
                   experiment_observer: Optional[ExperimentObserver] = None,
                   enable_feature_sweeping: bool = False,
                   verifier: Optional[VerifierManager] = None,
                   enable_cache: bool = True,
                   use_incremental_learning: bool = False) -> TransformedDataContext:
    """
    Transform input data from RawDataContext to TransformedDataContext.

    :param raw_data_context: The raw input data.
    :param preprocess: pre process data
    :param cache_store: the object that should be used to cache preprocessed data
    :param is_onnx_compatible: if works in onnx compatible mode
    :param logger: The logger
    :param experiment_observer: The experiment observer.
    :param enable_feature_sweeping: Enable or disable feature sweeping.
    :param use_incremental_learning: Whether run is using incremental learning.
    :return: Transformed data context.
    """
    if logger:
        logger.info("Pre-processing user data")

    if use_incremental_learning:
        return transform_data_streaming(raw_data_context, preprocess, logger, experiment_observer)

    if logger:
        logger.info("The size of raw data is: " + str(raw_data_context._get_memory_size()))

    if experiment_observer is None:
        experiment_observer = NullExperimentObserver()

    if raw_data_context.preprocess is None:
        raw_data_context.preprocess = preprocess

    y_df = raw_data_context.y
    if not isinstance(y_df, pd.DataFrame):
        y_df = pd.DataFrame(y_df)

    y_raw_stats = RawFeatureStats(y_df.iloc[:, 0])
    utilities._log_raw_data_stat(
        y_raw_stats,
        logger=logger,
        prefix_message="[YCol]"
    )

    x_is_sparse = scipy.sparse.issparse(raw_data_context.X)
    if raw_data_context.preprocess is False or raw_data_context.preprocess == "False" or x_is_sparse:
        # log the data characteristics as it won't going into pre-processing part.
        if x_is_sparse:
            if logger:
                logger.info("The sparse matrix is not supported for getting col charateristics.")
        else:
            x_df = raw_data_context.X
            if not isinstance(x_df, pd.DataFrame):
                x_df = pd.DataFrame(raw_data_context.X)
            for column in x_df.columns:
                raw_stats = RawFeatureStats(x_df[column])
                utilities._log_raw_data_stat(
                    raw_stats,
                    logger=logger,
                    prefix_message="[XColNum:{}]".format(x_df.columns.get_loc(column))
                )

    X, y, sample_weight = _remove_nan_rows_in_X_y(
        raw_data_context.X, raw_data_context.y,
        sample_weight=raw_data_context.sample_weight,
        logger=logger
    )
    X_valid, y_valid, sample_weight_valid = _remove_nan_rows_in_X_y(
        raw_data_context.X_valid, raw_data_context.y_valid,
        sample_weight=raw_data_context.sample_weight_valid,
        logger=logger
    )

    y_transformer, y, y_valid = _y_transform(y, y_valid, raw_data_context.task_type, logger)

    transformed_data_context = TransformedDataContext(X=X,
                                                      y=y,
                                                      X_valid=X_valid,
                                                      y_valid=y_valid,
                                                      sample_weight=sample_weight,
                                                      sample_weight_valid=sample_weight_valid,
                                                      x_raw_column_names=raw_data_context.x_raw_column_names,
                                                      cv_splits_indices=raw_data_context.cv_splits_indices,
                                                      num_cv_folds=raw_data_context.num_cv_folds,
                                                      validation_size=raw_data_context.validation_size,
                                                      timeseries=raw_data_context.timeseries,
                                                      timeseries_param_dict=raw_data_context.timeseries_param_dict,
                                                      cache_store=cache_store,
                                                      logger=logger)

    _log_data_info(logger=logger, X=transformed_data_context.X,
                   X_valid=transformed_data_context.X_valid,
                   y=transformed_data_context.y,
                   y_valid=transformed_data_context.y_valid)

    x_is_sparse = scipy.sparse.issparse(transformed_data_context.X)
    transformer, lag_transformer, ts_transformer = None, None, None
    data_sanpshot_str = None
    if ((raw_data_context.preprocess is False or raw_data_context.preprocess == "False") and
            raw_data_context.timeseries is False) or x_is_sparse:
        if logger:
            logger.info("No preprocessing of data to be done here")
        data_sanpshot_str = _get_data_snapshot(transformed_data_context.X)
    elif (raw_data_context.preprocess is True or raw_data_context.preprocess == "True")\
            and not raw_data_context.timeseries:
        transformed_data_context.X = _add_raw_column_names_to_X(raw_data_context.x_raw_column_names,
                                                                transformed_data_context.X)
        transformer, transformed_data_context.X, data_sanpshot_str = \
            _get_transformer_x(transformed_data_context.X,
                               transformed_data_context.y,
                               raw_data_context.task_type,
                               experiment_observer,
                               is_onnx_compatible,
                               enable_feature_sweeping,
                               logger,
                               verifier)

        if transformed_data_context.X_valid is not None:
            transformed_data_context.X_valid = _add_raw_column_names_to_X(
                raw_data_context.x_raw_column_names, transformed_data_context.X_valid)
            transformed_data_context.X_valid = transformer.transform(transformed_data_context.X_valid)

        if raw_data_context.lag_length is not None and raw_data_context.lag_length > 0:
            # Get engineered names from Data Transformer if available
            x_raw_column_names = np.asarray(raw_data_context.x_raw_column_names)
            if transformer is not None:
                x_raw_column_names = np.asarray(transformer.get_engineered_feature_names())

            # Create a lagging transformer
            lag_transformer = LaggingTransformer(raw_data_context.lag_length)

            # Fit/Transform using lagging transformer
            transformed_data_context.X = lag_transformer.fit_transform(
                _add_raw_column_names_to_X(x_raw_column_names, transformed_data_context.X),
                transformed_data_context.y)

            if transformed_data_context.X_valid is not None:
                transformed_data_context.X_valid = lag_transformer.transform(
                    _add_raw_column_names_to_X(x_raw_column_names,
                                               transformed_data_context.X_valid))
            if logger:
                logger.info(
                    "lagging transformer is enabled with length {}.".format(
                        raw_data_context.lag_length))

        transformed_data_context._set_transformer(x_transformer=transformer,
                                                  lag_transformer=lag_transformer)
    elif raw_data_context.timeseries is True:
        try:
            transformed_data_context.X = _add_raw_column_names_to_X(raw_data_context.x_raw_column_names,
                                                                    transformed_data_context.X)
            ts_transformer, transformed_data, data_sanpshot_str = \
                _get_ts_transformer_x(transformed_data_context.X,
                                      transformed_data_context.y,
                                      raw_data_context.timeseries_param_dict,
                                      for_cv=False,
                                      logger=logger,
                                      experiment_observer=experiment_observer)
            target_column_name = ts_transformer.target_column_name
            if raw_data_context.timeseries_param_dict is not None and target_column_name in transformed_data.columns:
                transformed_data_context.y = transformed_data.pop(target_column_name).values
                transformed_data_context.X = transformed_data
        except ValueError as e:
            raise DataException.from_exception(
                e,
                "Cannot preprocess time series data. Run after cleaning and processing manually.")
        except AzureMLForecastException as e:
            raise DataException.from_exception(
                e,
                "Timeseries transformation pipeline running into error. Run after cleaning and processing manually.")

        if transformed_data_context.X_valid is not None:
            try:
                transformed_data_context.X_valid = _add_raw_column_names_to_X(
                    raw_data_context.x_raw_column_names,
                    transformed_data_context.X_valid)
                transformed_data_valid = ts_transformer.transform(transformed_data_context.X_valid,
                                                                  transformed_data_context.y_valid)
                transformed_data_context.y_valid = transformed_data_valid.pop(target_column_name).values
                transformed_data_context.X_valid = transformed_data_valid.values
            except ValueError as e:
                raise DataException.from_exception(
                    e,
                    "Cannot preprocess time series validation data. Run after cleaning and processing manually.")
            except AzureMLForecastException as e:
                raise DataException.from_exception(
                    e,
                    "Timeseries transformation pipeline running into error. Run after cleaning and processing \
                        validation data manually.")

        transformed_data_context._set_transformer(ts_transformer=ts_transformer)

        if scipy.sparse.issparse(transformed_data_context.X):
            transformed_data_context.X = transformed_data_context.X.todense()
    else:
        if logger:
            logger.info(
                "lagging transformer is enabled with length {}.".format(raw_data_context.lag_length))

    transformed_data_context._set_raw_data_snapshot_str(data_sanpshot_str)
    transformed_data_context._set_transformer(transformer, lag_transformer, y_transformer=y_transformer,
                                              ts_transformer=ts_transformer)

    # Create featurized versions of cross validations if user configuration specifies cross validations
    _create_cv_splits_transformed_data(transformed_data_context, raw_data_context,
                                       X, y, sample_weight,
                                       experiment_observer,
                                       logger)

    # Refit transformers
    raw_X = _add_raw_column_names_to_X(raw_data_context.x_raw_column_names, X)

    transformed_data_context._refit_transformers(raw_X, y)

    if isinstance(transformed_data_context.X, pd.DataFrame):
        # X should be a numpy array
        transformed_data_context.X = transformed_data_context.X.values

    if enable_cache or raw_data_context.preprocess or raw_data_context.timeseries:
        transformed_data_context._update_cache()

    if logger:
        logger.info("The size of transformed data is: " + str(transformed_data_context._get_memory_size()))

    return transformed_data_context


def transform_data_streaming(raw_data_context: RawDataContext,
                             preprocess: bool,
                             logger: Optional[logging.Logger] = None,
                             observer: Optional[ExperimentObserver] = None) -> TransformedDataContext:
    """
    Transform the input from RawDataContext to TransformedDataContext in a streaming fashion.

    :param raw_data_context: The raw input data.
    :return: Transformed data context.
    """
    X = raw_data_context.X
    X_valid = raw_data_context.X_valid

    if preprocess:
        streaming_featurizer = StreamingFeaturizer(logger, observer)
        # todo these are dataflows, make sure to convert to pickleable in tx_data_context -> add_to_cache()
        X = streaming_featurizer.featurize_dataflow(raw_data_context.X)
        X_valid = streaming_featurizer.featurize_dataflow(raw_data_context.X_valid)

    # todo revisit the concept of having a 'TransformedDataContext'
    return TransformedDataContext(
        X=X,
        y=raw_data_context.y,
        X_valid=X_valid,
        y_valid=raw_data_context.y_valid,
        sample_weight=raw_data_context.sample_weight,
        sample_weight_valid=raw_data_context.sample_weight_valid,
        x_raw_column_names=raw_data_context.x_raw_column_names,
        cv_splits_indices=raw_data_context.cv_splits_indices,
        num_cv_folds=raw_data_context.num_cv_folds,
        validation_size=raw_data_context.validation_size,
        timeseries=raw_data_context.timeseries,
        timeseries_param_dict=raw_data_context.timeseries_param_dict)


def _log_data_info(logger: Optional[logging.Logger],
                   X: np.ndarray,
                   y: np.ndarray,
                   X_valid: np.ndarray,
                   y_valid: np.ndarray) -> None:
    """
    Log data details.

    :param logger:
    :param X:
    :param y:
    :param X_valid:
    :param y_valid:
    """

    if logger is None:
        return

    # logging X and y info
    logger.info(
        "X datatype is {}, shape is {}, datasize is {}.".format(
            type(X), X.shape, memory_utilities.get_data_memory_size(X)
        )
    )
    logger.info(
        "y datatype is {}, shape is {}, datasize is {}.".format(
            type(y), y.shape, memory_utilities.get_data_memory_size(y)
        )
    )
    if X_valid is not None:
        logger.info(
            "X_valid datatype is {}, shape is {}, datasize is {}.".format(
                type(X_valid),
                X_valid.shape, memory_utilities.get_data_memory_size(X_valid)
            )
        )
    if y_valid is not None:
        logger.info(
            "y_valid datatype is {}, shape is {}, datasize is {}.".format(
                type(y_valid),
                y_valid.shape, memory_utilities.get_data_memory_size(y_valid)
            )
        )


def _get_data_snapshot(data: DataInputType, is_forecasting: bool = False) -> Any:
    if data is None:
        raise DataException("Data is not valid")
    try:
        if isinstance(data, pd.DataFrame):
            if is_forecasting:
                first_row = data[:1]
                first_row['y_query'] = 1.0
                df_str = first_row.to_json(orient='records', date_format='iso')
            else:
                df_str = data[:1].to_json(orient='records', date_format='iso')
            sample_df_str = 'pd.DataFrame(data=' + df_str + ')'
            return sample_df_str
        elif isinstance(data, np.ndarray):
            np_array_str = pd.Series(data[0]).to_json(orient='values', date_format='iso')
            sample_numpy_array_str = 'np.array([' + np_array_str + '])'
            return sample_numpy_array_str
        elif scipy.sparse.issparse(data):
            # Assuming that sparse matrix will be inferenced as a numpy array
            # TODO: Test sparse matrices with inference scenario
            np_array_str = pd.Series(data[0, :].toarray().ravel()).to_json(orient='values', date_format='iso')
            sample_sparse_array_str = 'np.array([' + np_array_str + '])'
            return sample_sparse_array_str
        else:
            raise DataException("Data format is not recognized")
    except DataException as e:
        raise e
    except Exception as e:
        exception_error_msg = "Raw data sanpshot failed with error: {error}".format(error=e)
        raise RawDataSnapshotException(exception_error_msg)


def _get_transformer_x(x: DataInputType, y: np.ndarray, task_type: str,
                       experiment_observer: ExperimentObserver, is_onnx_compatible: bool = False,
                       enable_feature_sweeping: bool = False, logger: Optional[logging.Logger] = None,
                       verifier: Optional[VerifierManager] = None) -> Tuple[DataTransformer, Any, str]:
    """
    Given data, compute transformations and transformed data.

    :param x: input data
    :param y: labels
    :param task_type: one of the tasks defined in constants.Tasks
    :param is_onnx_compatible: if works in onnx compatible mode
    :param logger: logger object for logging data from pre-processing
    :return: transformer, transformed_x
    """
    dt = DataTransformer(task_type, is_onnx_compatible=is_onnx_compatible,
                         enable_feature_sweeping=enable_feature_sweeping, observer=experiment_observer)

    if experiment_observer is not None:
        experiment_observer.report_status(
            ExperimentStatus.DatasetFeaturization, "Beginning to featurize the dataset.")

    data_sanpshot_str = _get_data_snapshot(x)
    x_transform = dt.fit_transform_with_logger(x, y, logger)

    if verifier is not None:
        verifier.update_data_verifier_from_transformer(dt)
        verifier.update_data_verifier_for_text_class_validation(dt.stats_and_column_purposes)

    if experiment_observer is not None:
        experiment_observer.report_status(
            ExperimentStatus.DatasetFeaturizationCompleted, "Completed featurizing the dataset.")

    return dt, x_transform, data_sanpshot_str


def _get_ts_transformer_x(x, y, timeseries_param_dict, for_cv=False, logger=None, experiment_observer=None):
    """
    Given data, compute transformations and transformed data.

    :param x: input data
    :param y: labels
    :param timeseries_param_dict: timeseries metadata
    :param logger: logger object for logging data from pre-processing
    :return: transformer, transformed_x
    """
    pipeline_type = TimeSeriesPipelineType.CV_REDUCED if for_cv else TimeSeriesPipelineType.FULL
    tst = TimeSeriesTransformer(pipeline_type=pipeline_type, logger=logger, **timeseries_param_dict)

    if experiment_observer is not None:
        message = 'Beginning to featurize the CV split.' if for_cv else 'Beginning to featurize the dataset.'
        experiment_observer.report_status(
            ExperimentStatus.DatasetFeaturization, message)

    data_sanpshot_str = _get_data_snapshot(x, is_forecasting=True)
    x_transform = tst.fit_transform(x, y)

    if experiment_observer is not None:
        message = 'Completed featurizing the CV split.' if for_cv else 'Completed featurizing the dataset.'
        experiment_observer.report_status(
            ExperimentStatus.DatasetFeaturizationCompleted, message)

    return tst, x_transform, data_sanpshot_str


def _add_raw_column_names_to_X(x_raw_column_names: np.ndarray, X: DataInputType) -> DataInputType:
    """
    Add raw column names to X.

    :param x_raw_column_names: List of raw column names
    :param X: dataframe / array
    :raise ValueError if number of raw column names is not same as the number of columns in X
    :return: Dataframe with column names
    """
    # Combine the raw feature names with X
    if x_raw_column_names is not None:
        if x_raw_column_names.shape[0] != X.shape[1]:
            raise DataException("Number of raw column names {} and number of columns in input data {} do not match"
                                .format(x_raw_column_names.shape[0], X.shape[1]))
        if isinstance(X, pd.DataFrame):
            # If X is already a DataFrame, then return X. Assumption here is that raw column names
            # are already present in the data frame header. The passed x_raw_column_names are not
            # needed.
            return X
        if not scipy.sparse.issparse(X):
            X_with_raw_columns = pd.DataFrame(
                data=X, columns=x_raw_column_names.tolist())
            return X_with_raw_columns
        else:
            X_with_raw_columns = pd.SparseDataFrame(
                data=X, columns=x_raw_column_names.tolist())
            return X_with_raw_columns

    return X


def _y_transform(y, y_valid, task_type, logger=None):
    """
    Apply label encoder for string, float and negative int type y data.

    :param y: y data
    :param y_valid: Validation y data
    :param task_type: CLASSIFICATION/REGRESSION
    :return:
    """
    y_transformer = None
    if task_type == constants.Tasks.CLASSIFICATION and (
       not utilities._check_if_column_data_type_is_int(utilities._get_column_data_type_as_str(y)) or np.amin(y) < 0):
        # Currently y_transformer only support the label encoder for negative, float and categorical data.
        if logger is not None:
            logger.info("Start doing label encoding on y data.")
        y_transformer = preprocessing.LabelEncoder()
        if y_valid is None:
            le = y_transformer.fit(y)
            y = le.transform(y)
        else:
            le = y_transformer.fit(np.vstack([y.reshape(-1, 1), y_valid.reshape(-1, 1)]))
            y = le.transform(y)
            y_valid = le.transform(y_valid)
        if logger is not None:
            logger.info("End doing label encoding on y data.")
    return y_transformer, y, y_valid


def _remove_nan_rows_in_X_y(X, y, sample_weight=None, logger=None):
    """Remove the NaN columns in y and the corresponding rows in X."""
    X_new = X
    y_new = y
    sample_weight_new = sample_weight

    if X is not None and y is not None:
        nan_y_index = utilities._get_indices_missing_labels_output_column(y)

        if len(nan_y_index) > 0:
            if logger is not None:
                logger.info("Start removing NaN labels in y data.")
            y_new = np.delete(y, nan_y_index)
            if scipy.sparse.issparse(X):
                X_new = X_new.toarray()
            if isinstance(X_new, pd.DataFrame):
                X_new = X_new.loc[set(range(X_new.shape[0])) - set(nan_y_index)]
            else:
                X_new = np.delete(X, nan_y_index, axis=0)
            if sample_weight is not None:
                if scipy.sparse.issparse(sample_weight):
                    sample_weight_new = sample_weight_new.toarray()
                sample_weight_new = np.delete(sample_weight, nan_y_index, axis=0)
            # if input is sparse, convert back to csr
            if scipy.sparse.issparse(X):
                X_new = scipy.sparse.csr_matrix(X_new)
            if scipy.sparse.issparse(sample_weight):
                sample_weight_new = scipy.sparse.csr_matrix(sample_weight_new)
            if logger is not None:
                logger.info("End removing NaN labels in y data.")
    return X_new, y_new, sample_weight_new


def _create_cv_splits_transformed_data(transformed_data_context: TransformedDataContext,
                                       raw_data_context: RawDataContext, X: np.ndarray, y: np.ndarray,
                                       sample_weight: Optional[np.ndarray],
                                       experiment_observer: ExperimentObserver,
                                       logger: Optional[logging.Logger] = None) -> None:
    """
    Create featurized data for individual CV splits using the data transformer and lagging trransformer.

    :param raw_data_context: The raw data context.
    :param X: Raw training data
    :param y: Raw output variable data
    :param sample_weight: Sample weight
    :param logger: logger for logging
    :return:
    """
    # Check if CV splits need to featurized
    if transformed_data_context.num_cv_folds is not None or \
        (transformed_data_context.validation_size is not None and
         transformed_data_context.validation_size > 0.0) or \
            transformed_data_context.cv_splits_indices is not None:

        if logger:
            logger.info("Creating cross validations")

        if raw_data_context.preprocess is False or raw_data_context.preprocess == "False":
            experiment_observer.report_status(
                ExperimentStatus.DatasetCrossValidationSplit,
                "Generating CV splits.")
        else:
            experiment_observer.report_status(
                ExperimentStatus.DatasetCrossValidationSplit,
                "Generating individually featurized CV splits.")

        # Add raw column names to raw training data
        raw_X = _add_raw_column_names_to_X(raw_data_context.x_raw_column_names, X)
        raw_y = y

        # Create CV splits object
        transformed_data_context.cv_splits = \
            _CVSplits(raw_X, raw_y,
                      frac_valid=transformed_data_context.validation_size,
                      CV=transformed_data_context.num_cv_folds,
                      cv_splits_indices=transformed_data_context.cv_splits_indices,
                      is_time_series=raw_data_context.timeseries,
                      timeseries_param_dict=raw_data_context.timeseries_param_dict)

        if logger:
            logger.info("Found cross validation type: " + str(transformed_data_context.cv_splits._cv_split_type))

        # If data transformer or lagging transformers are valid, then featurize individual CV splits
        if transformed_data_context.transformers[constants.Transformers.X_TRANSFORMER] is not None or \
                transformed_data_context.transformers[constants.Transformers.LAG_TRANSFORMER] is not None or \
                transformed_data_context.transformers[constants.Transformers.TIMESERIES_TRANSFORMER] is not None:

            data_transformer = transformed_data_context.transformers[constants.Transformers.X_TRANSFORMER]
            lag_transformer = transformed_data_context.transformers[constants.Transformers.LAG_TRANSFORMER]
            ts_transformer = transformed_data_context.transformers[constants.Transformers.TIMESERIES_TRANSFORMER]

            if transformed_data_context.cv_splits.get_cv_split_indices() is not None:
                if logger:
                    logger.info("Creating featurized version of CV splits data")

                # Walk all CV split indices and featurize individual train and validation set pair
                transformed_data_context.cv_splits._featurized_cv_splits = []
                cv_split_index = 0
                for X_train, y_train, sample_wt_train, X_test, y_test, sample_wt_test \
                        in transformed_data_context.cv_splits.apply_CV_splits(raw_X, raw_y, sample_weight):

                    if data_transformer is not None:
                        X_train = data_transformer.fit_transform(X_train, y_train)
                        X_test = data_transformer.transform(X_test)

                    if lag_transformer is not None:
                        X_train = lag_transformer.fit_transform(X_train, y_train)
                        X_test = lag_transformer.transform(X_test)

                    if ts_transformer is not None:
                        assert raw_data_context.timeseries_param_dict is not None,\
                            "Expected non-none timeseries parameter dict"  # ensure type is correct for mypy
                        # Need to do pipeline introspection on ts_transformer for CV featurization.
                        # For compatibility with old SDK versions, re-compute the ts_transformer feature graph
                        # if it is not set
                        ts_transformer._create_feature_transformer_graph_if_not_set(raw_X, y=raw_y)

                        # Get list of time index features used on full train set fit
                        non_holiday_features = ts_transformer.time_index_non_holiday_features
                        ts_split_param_dict = raw_data_context.timeseries_param_dict.copy()
                        ts_split_param_dict[constants.TimeSeriesInternal.FORCE_TIME_INDEX_FEATURES_NAME] = \
                            non_holiday_features

                        ts_split_transformer, X_train, _ = \
                            _get_ts_transformer_x(X_train, y_train, ts_split_param_dict,
                                                  for_cv=True, logger=logger,
                                                  experiment_observer=experiment_observer)

                        # Join with full featurized set to get re-useable features
                        X_train = \
                            TimeSeriesTransformer._join_reusable_features_for_cv(ts_split_transformer, X_train,
                                                                                 ts_transformer,
                                                                                 transformed_data_context.X)

                        if ts_split_transformer.target_column_name in X_train.columns:
                            y_train = X_train.pop(ts_split_transformer.target_column_name).values

                        X_test = ts_split_transformer.transform(X_test, y_test)
                        X_test = \
                            TimeSeriesTransformer._join_reusable_features_for_cv(ts_split_transformer, X_test,
                                                                                 ts_transformer,
                                                                                 transformed_data_context.X)

                        # Need to apply some corrections when data has horizon-dependent features (i.e. Lags/RW)
                        if ts_transformer.origin_column_name in X_test.index.names:
                            # X_test may have some origin times later than the latest known train times
                            latest_known_dates = \
                                {gr: df.index.get_level_values(ts_transformer.time_column_name).max()
                                 for gr, df in X_train.groupby(ts_transformer.grain_column_names)}
                            X_test = (X_test.groupby(ts_transformer.grain_column_names, group_keys=False)
                                      .apply(lambda df:
                                             ts_transformer._select_known_before_date(df, latest_known_dates[df.name],
                                                                                      ts_transformer.freq_offset)))

                            # To match forecasting logic, select predictions made from most recent origin times
                            X_test = ts_transformer._select_latest_origin_dates(X_test)
                        if ts_split_transformer.target_column_name in X_test.columns:
                            y_test = X_test.pop(ts_split_transformer.target_column_name).values

                    # Create the featurized CV split object
                    featurized_cv = FeaturizedCVSplit(
                        X_train, y_train, sample_wt_train,
                        X_test, y_test, sample_wt_test, None, None)

                    if logger:
                        logger.info(str(featurized_cv))

                    # Flush the featurized data on the cache store
                    transformed_data_context._update_cache_with_featurized_data(
                        TransformedDataContext.FEATURIZED_CV_SPLIT_KEY_INITIALS +
                        str(cv_split_index), featurized_cv)

                    # Clear the in-memory data for the featurized data and record the cache store and key
                    featurized_cv._clear_featurized_data_and_record_cache_store(
                        transformed_data_context.cache_store,
                        TransformedDataContext.FEATURIZED_CV_SPLIT_KEY_INITIALS + str(cv_split_index))

                    cv_split_index += 1

                    # Append to the list of featurized CV splits
                    transformed_data_context.cv_splits._featurized_cv_splits.append(featurized_cv)

            else:
                if logger:
                    logger.info("Creating featurized data for train and validation data")

                if raw_data_context.timeseries:
                    raise DataException('Could not retrieve CV splits for time-series data. ' +
                                        'Please set the number of cross-validation folds.')

                X_train, y_train, sample_weight_train, X_valid, y_valid, \
                    sample_weight_valid, _, _, _ = \
                    transformed_data_context.cv_splits.get_train_validation_test_chunks(raw_X, raw_y, sample_weight)

                if data_transformer is not None:
                    if X_train is not None:
                        X_train = data_transformer.fit_transform(X_train, y_train)
                    if X_valid is not None:
                        X_valid = data_transformer.transform(X_valid)

                if lag_transformer is not None:
                    if X_train is not None:
                        X_train = lag_transformer.fit_transform(X_train, y_train)
                    if X_valid is not None:
                        X_valid = lag_transformer.transform(X_valid)

                # Create the featurized train, valid and test object
                featurized_train_test_valid = FeaturizedTrainValidTestSplit(
                    X_train, y_train, sample_weight_train,
                    X_valid, y_valid, sample_weight_valid,
                    None, None, None, None, None)

                if logger:
                    logger.info(str(featurized_train_test_valid))

                # Flush the featurized data on the cache store
                transformed_data_context._update_cache_with_featurized_data(
                    TransformedDataContext.FEATURIZED_TRAIN_TEST_VALID_KEY_INITIALS,
                    featurized_train_test_valid)

                # Clear the in-memory data for the featurized data and record the cache store and key
                featurized_train_test_valid._clear_featurized_data_and_record_cache_store(
                    transformed_data_context.cache_store,
                    TransformedDataContext.FEATURIZED_TRAIN_TEST_VALID_KEY_INITIALS)

                transformed_data_context.cv_splits._featurized_train_test_valid_chunks = featurized_train_test_valid

        if logger:
            logger.info("Completed creating cross-validation folds and featurizing them")
