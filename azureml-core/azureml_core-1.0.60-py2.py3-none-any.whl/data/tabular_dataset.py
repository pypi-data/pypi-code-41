# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains class that represents tabular dataset to use in Azure Machine Learning service."""

from datetime import datetime
from azureml.data._dataset import _Dataset
from azureml.data._loggerfactory import track, _LoggerFactory
from azureml.data.constants import _PUBLIC_API, _DATASET_PROP_TIMESTAMP_FINE, _DATASET_PROP_TIMESTAMP_COARSE
from azureml.data.dataset_error_handling import _validate_has_data, _validate_has_columns, _try_execute
from azureml.data._dataprep_helper import dataprep
from azureml.exceptions import DatasetTimestampMissingError

_logger = None


def _get_logger():
    global _logger
    if _logger is not None:
        return _logger
    _logger = _LoggerFactory.get_logger(__name__)
    return _logger


class TabularDataset(_Dataset):
    """The class that represents tabular dataset to use in Azure Machine Learning service.

    A TabularDataset defines a series of lazily-evaluated, immutable operations to load data from the
    data source into tabular representation.

    Data is not loaded from the source until TabularDataset is asked to deliver data.

    .. remarks::

        TabularDataset is created using methods like
        :func:`azureml.data.dataset_factory.TabularDatasetFactory.from_delimited_files` from
        :class:`azureml.data.dataset_factory.TabularDatasetFactory` class.

        TabularDataset can be used as input of an experiment run. It can also be registered to workspace
        with a specified name and be retrieved by that name later.

        TabularDataset can be subsetted by invoking different subsetting methods available on this class.
        The result of subsetting is always a new TabularDataset.

        The actual data loading happens when TabularDataset is asked to deliver the data into another
        storage mechanism (e.g. a Pandas Dataframe, or a CSV file).
    """

    def __init__(self):
        """Initialize a TabularDataset object.

        This constructor is not supposed to be invoked directly. Dataset is intended to be created using
        :class:`azureml.data.dataset_factory.TabularDatasetFactory` class.
        """
        super().__init__()

    @property
    @track(_get_logger, activity_type=_PUBLIC_API)
    def timestamp_columns(self):
        """Return the timestamp columns.

        :return: The column names for fine_grain_timestamp and coarse_grain_timestamp defined for the dataset.
        :rtype: (str, str)
        """
        fine_grain_timestamp = self._properties.get(_DATASET_PROP_TIMESTAMP_FINE, None)
        coarse_grain_timestamp = self._properties.get(_DATASET_PROP_TIMESTAMP_COARSE, None)
        return (fine_grain_timestamp, coarse_grain_timestamp)

    @track(_get_logger, activity_type=_PUBLIC_API)
    def with_timestamp_columns(self, fine_grain_timestamp, coarse_grain_timestamp=None, validate=False):
        """Define timestamp columns for the dataset.

        .. remarks::

            Define the columns to be used as timestamps. Timestamp columns on a dataset make it possible
            to treat the data as time-series data and enables additional capabilities. When a dataset has
            both fine_grain_timestamp and coarse_grain_timestamp defined, the two columns should represent
            the same timeline.

        :param fine_grain_timestamp: The name of column as fine grain timestamp, use None to clear it.
        :type fine_grain_timestamp: str
        :param coarse_grain_timestamp: The name of column coarse grain timestamp (optional). Default is None (clear).
        :type coarse_grain_timestamp: str
        :param validate: Boolean to validate if specified columns exist in dataset. Defaults to False.
            Validation requires that the data source is accessible from the current compute.
        :type validate: bool
        :return: Returns a new TabularDataset with timestamp columns defined.
        :rtype: azureml.data.TabularDataset
        """
        if not fine_grain_timestamp and coarse_grain_timestamp:
            raise ValueError('Cannot assign coarse_grain_timestamp separately while fine_grain_timestamp is None.')
        if fine_grain_timestamp and fine_grain_timestamp == coarse_grain_timestamp:
            raise ValueError('coarse_grain_timestamp cannot be the same as fine_grain_timestamp.')
        if validate:
            self._validate_timestamp_columns([fine_grain_timestamp, coarse_grain_timestamp])

        dataset = TabularDataset._create(self._dataflow, self._properties)

        if fine_grain_timestamp:
            dataset._properties[_DATASET_PROP_TIMESTAMP_FINE] = fine_grain_timestamp
        else:
            if _DATASET_PROP_TIMESTAMP_FINE in self._properties:
                del dataset._properties[_DATASET_PROP_TIMESTAMP_FINE]

        if coarse_grain_timestamp:
            dataset._properties[_DATASET_PROP_TIMESTAMP_COARSE] = coarse_grain_timestamp
        else:
            if _DATASET_PROP_TIMESTAMP_COARSE in self._properties:
                del dataset._properties[_DATASET_PROP_TIMESTAMP_COARSE]
        return dataset

    @track(_get_logger, activity_type=_PUBLIC_API)
    def to_pandas_dataframe(self):
        """Load all records from the dataset into a pandas DataFrame.

        :return: Returns a pandas DataFrame.
        :rtype: pandas.DataFrame
        """
        return _try_execute(self._dataflow.to_pandas_dataframe)

    @track(_get_logger, activity_type=_PUBLIC_API)
    def to_spark_dataframe(self):
        """Load all records from the dataset into a spark DataFrame.

        :return: Returns a spark DataFrame.
        :rtype: pyspark.sql.DataFrame
        """
        return _try_execute(self._dataflow.to_spark_dataframe)

    @track(_get_logger, activity_type=_PUBLIC_API)
    def skip(self, count):
        """Skip records from top of the dataset by the specified count.

        :param count: The number of records to skip.
        :type count: int
        :return: Returns a new TabularDataset object for the dataset with record skipped.
        :rtype: azureml.data.TabularDataset
        """
        return TabularDataset._create(self._dataflow.skip(count), self._properties)

    @track(_get_logger, activity_type=_PUBLIC_API)
    def take(self, count):
        """Take a sample of records from top of the dataset by the specified count.

        :param count: The number of records to take.
        :type count: int
        :return: Returns a new TabularDataset object for the sampled dataset.
        :rtype: azureml.data.TabularDataset
        """
        return TabularDataset._create(self._dataflow.take(count), self._properties)

    @track(_get_logger, activity_type=_PUBLIC_API)
    def take_sample(self, probability, seed=None):
        """Take a random sample of records in the dataset approximately by the probability specified.

        :param probability: The probability of a record being included in the sample.
        :type probability: float
        :param seed: Optional seed to use for the random generator.
        :type seed: int
        :return: Returns a new TabularDataset object for the sampled dataset.
        :rtype: azureml.data.TabularDataset
        """
        return TabularDataset._create(self._dataflow.take_sample(probability, seed), self._properties)

    @track(_get_logger, activity_type=_PUBLIC_API)
    def random_split(self, percentage, seed=None):
        """Split records in the dataset into two parts randomly and approximately by the percentage specified.

        :param percentage: The approximate percentage to split the Dataflow by. This must be a number between
            0.0 and 1.0.
        :type percentage: float
        :param seed: Optional seed to use for the random generator.
        :type seed: int
        :return: Returns a tuple of new TabularDataset objects for the tow split datasets.
        :rtype: (azureml.data.TabularDataset, azureml.data.TabularDataset)
        """
        dataflow1, dataflow2 = self._dataflow.random_split(percentage, seed)
        return (
            TabularDataset._create(dataflow1, self._properties),
            TabularDataset._create(dataflow2, self._properties)
        )

    @track(_get_logger, activity_type=_PUBLIC_API)
    def keep_columns(self, columns, validate=False):
        """Keep the specified columns and drops all others from the dataset.

        :param columns: The name or a list of names for the columns to keep.
        :type columns: str or List[str]
        :param validate: Boolean to validate if data can be loaded from the returned dataset. Defaults to True.
            Validation requires that the data source is accessible from current compute.
        :type validate: bool
        :return: Returns a new TabularDataset object for dataset with only the specified columns kept.
        :rtype: azureml.data.TabularDataset
        """
        for col in list(filter(lambda x: x is not None, self.timestamp_columns)):
            if col not in columns:
                error_message = "Column {} should be included because it's a timestamp column".format(col)
                raise ValueError(error_message)

        dataflow = self._dataflow.keep_columns(columns, validate_column_exists=False)
        if validate:
            _validate_has_data(dataflow,
                               ('Cannot load any data from the dataset with only columns {} kept. ' +
                                'Make sure the specified columns exist in the current dataset.')
                               .format(columns if isinstance(columns, list) else [columns]))
        return TabularDataset._create(dataflow, self._properties)

    @track(_get_logger, activity_type=_PUBLIC_API)
    def drop_columns(self, columns):
        """Drop the specified columns from the dataset.

        :param columns: The name or a list of names for the columns to drop.
        :type columns: str or List[str]
        :return: Returns a new TabularDataset object for dataset with the specified columns dropped.
        :rtype: azureml.data.TabularDataset
        """
        for col in list(filter(lambda x: x is not None, self.timestamp_columns)):
            if col in columns:
                error_message = "Column {} should not be dropped because it's a timestamp column. " \
                                "Please exclude it or use with_timestamp_columns with value None to reset it " \
                                "before dropping columns.".format(col)
                raise ValueError(error_message)

        return TabularDataset._create(self._dataflow.drop_columns(columns), self._properties)

    @track(_get_logger, activity_type=_PUBLIC_API)
    def to_parquet_files(self):
        """Convert the current dataset into a FileDataset containing Parquet files.

        The resulting dataset will contain one or more Parquet files, each corresponding to a partition of data
        from the current dataset. These files are not materialized until they are downloaded or read from.

        :return: Returns a new FileDataset object with a set of Parquet files containing the data in this dataset.
        :rtype: azureml.data.FileDataset
        """
        from azureml.data.file_dataset import FileDataset
        parquet_dataflow = self._dataflow.to_parquet_streams()
        return FileDataset._create(parquet_dataflow)

    @track(_get_logger, activity_type=_PUBLIC_API)
    def to_csv_files(self, separator=','):
        """Convert the current dataset into a FileDataset containing CSV files.

        The resulting dataset will contain one or more CSV files, each corresponding to a partition of data
        from the current dataset. These files are not materialized until they are downloaded or read from.

        :param separator: The separator to use to separate values in the resulting file.
        :type separator: str
        :return: Returns a new FileDataset object with a set of CSV files containing the data in this dataset.
        :rtype: azureml.data.FileDataset
        """
        from azureml.data.file_dataset import FileDataset
        csv_dataflow = self._dataflow.to_csv_streams(separator=separator)
        return FileDataset._create(csv_dataflow)

    @track(_get_logger, activity_type=_PUBLIC_API)
    def time_before(self, end_time, include_boundary=False):
        """Filter TabularDataset with time stamp columns before a specified end time.

        :param end_time: Upper bound for filtering data.
        :type end_time: datetime.datetime
        :param include_boundary: indicate if row associated with the boundary time (end_time) should be included.
        :type include_boundary: bool
        :return: A TabularDataset with the new filtered data
        :rtype: azureml.data.TabularDataset
        """
        return self._time_filter(self.time_before.__name__,
                                 upper_bound=end_time, include_boundary=include_boundary)

    @track(_get_logger, activity_type=_PUBLIC_API)
    def time_after(self, start_time, include_boundary=False):
        """Filter TabularDataset with time stamp columns after a specified start time.

        :param start_time: Lower bound for filtering data.
        :type start_time: datetime.datetime
        :param include_boundary: indicate if row associated with the boundary time (start_time) should be included.
        :type include_boundary: bool
        :return: A TabularDataset with the new filtered data
        :rtype: azureml.data.TabularDataset
        """
        return self._time_filter(self.time_after.__name__,
                                 lower_bound=start_time, include_boundary=include_boundary)

    @track(_get_logger, activity_type=_PUBLIC_API)
    def time_recent(self, time_delta, include_boundary=False):
        """Filter TabularDataset to contain only the most recent data specified by time_delta.

        :param time_delta: Amount of recent data to retrieve.
        :type time_delta: datetime.timedelta
        :param include_boundary: indicate if row associated with the boundary time (now-time_delta) should be included.
        :type include_boundary: bool
        :return: A TabularDataset with the new filtered data
        :rtype: azureml.data.TabularDataset
        """
        start_time = datetime.now() - time_delta
        return self._time_filter(self.time_recent.__name__,
                                 lower_bound=start_time, include_boundary=include_boundary)

    @track(_get_logger, activity_type=_PUBLIC_API)
    def time_between(self, start_time, end_time, include_boundary=False):
        """Filter TabularDataset between a specified start and end time.

        :param start_time: Lower bound for filtering data.
        :type start_time: datetime.datetime
        :param end_time: Upper bound for filtering data.
        :type end_time: datetime.datetime
        :param include_boundary: indicate if row associated with the boundary time (start/end_time) should be included.
        :type include_boundary: bool
        :return: A TabularDataset with the new filtered data
        :rtype: azureml.data.TabularDataset
        """
        return self._time_filter(self.time_between.__name__,
                                 lower_bound=start_time, upper_bound=end_time, include_boundary=include_boundary)

    def _time_filter(self, method, lower_bound=None, upper_bound=None, include_boundary=False):
        exception_message = 'Cannot perform time-series filter `{}` on dataset without timestamp columns defined.' \
                            'Please use `with_timestamp_columns` to enable time-series capabilities'.format(method)

        if self._properties is None \
                or _DATASET_PROP_TIMESTAMP_FINE not in self._properties \
                or self._properties[_DATASET_PROP_TIMESTAMP_FINE] is None:
            raise DatasetTimestampMissingError(error_details=exception_message)

        col_fine_timestamp = self._properties[_DATASET_PROP_TIMESTAMP_FINE]
        col_coarse_timestamp = None
        if _DATASET_PROP_TIMESTAMP_COARSE in self._properties \
                and self._properties[_DATASET_PROP_TIMESTAMP_COARSE] is not None:
            col_coarse_timestamp = self._properties[_DATASET_PROP_TIMESTAMP_COARSE]

        # validate column type are datetime
        self._validate_timestamp_columns([col_fine_timestamp, col_coarse_timestamp])

        dataflow = self._dataflow

        # base filter, will enrich filters in following steps.
        from azureml.dataprep import Expression
        filters = Expression(dataflow[col_fine_timestamp] is not None)

        if lower_bound is not None:
            # coarse timestamp may not be assigned.
            if col_coarse_timestamp is not None:
                filter_coarse_lower = dataflow[col_coarse_timestamp] >= lower_bound if include_boundary \
                    else dataflow[col_coarse_timestamp] > lower_bound
                filters &= filter_coarse_lower
            # fine timestamp is guaranteed to be there.
            filter_fine_lower = dataflow[col_fine_timestamp] >= lower_bound if include_boundary \
                else dataflow[col_fine_timestamp] > lower_bound
            filters &= filter_fine_lower

        if upper_bound is not None:
            # coarse timestamp may not be assigned.
            if col_coarse_timestamp is not None:
                filter_coarse_upper = dataflow[col_coarse_timestamp] <= upper_bound if include_boundary \
                    else dataflow[col_coarse_timestamp] < upper_bound
                filters &= filter_coarse_upper
            # fine timestamp is guaranteed to be there.
            filter_fine_upper = dataflow[col_fine_timestamp] <= upper_bound if include_boundary \
                else dataflow[col_fine_timestamp] < upper_bound
            filters &= filter_fine_upper

        result = dataflow.filter(filters)

        return TabularDataset._create(result, self._properties)

    def _validate_timestamp_columns(self, columns_list):
        FieldType = dataprep().api.engineapi.typedefinitions.FieldType
        columns = list(filter(lambda col: col is not None, columns_list))
        _validate_has_columns(self._dataflow, columns, [FieldType.DATE for c in columns])
