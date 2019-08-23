# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains class that represents tabular dataset to use in Azure Machine Learning service."""

from azureml.data._dataset import _Dataset
from azureml.data._loggerfactory import track, _LoggerFactory
from azureml.data.constants import _PUBLIC_API
from azureml.data.dataset_error_handling import _validate_has_data, _try_execute


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
        return TabularDataset._create(self._dataflow.skip(count))

    @track(_get_logger, activity_type=_PUBLIC_API)
    def take(self, count):
        """Take a sample of records from top of the dataset by the specified count.

        :param count: The number of records to take.
        :type count: int
        :return: Returns a new TabularDataset object for the sampled dataset.
        :rtype: azureml.data.TabularDataset
        """
        return TabularDataset._create(self._dataflow.take(count))

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
        return TabularDataset._create(self._dataflow.take_sample(probability, seed))

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
            TabularDataset._create(dataflow1),
            TabularDataset._create(dataflow2)
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
        dataflow = self._dataflow.keep_columns(columns, validate_column_exists=False)
        if validate:
            _validate_has_data(dataflow,
                               ('Cannot load any data from the dataset with only columns {} kept. ' +
                                'Make sure the specified columns exist in the current dataset')
                               .format(columns if isinstance(columns, list) else [columns]))
        return TabularDataset._create(dataflow)

    @track(_get_logger, activity_type=_PUBLIC_API)
    def drop_columns(self, columns):
        """Drop the specified columns from the dataset.

        :param columns: The name or a list of names for the columns to drop.
        :type columns: str or List[str]
        :return: Returns a new TabularDataset object for dataset with the specified columns dropped.
        :rtype: azureml.data.TabularDataset
        """
        return TabularDataset._create(self._dataflow.drop_columns(columns))
