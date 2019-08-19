# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Classes to create dataset for Azure Machine Learning service."""

import re
import warnings
from azureml.data.abstract_datastore import AbstractDatastore
from azureml.data.constants import _PUBLIC_API
from azureml.data.datapath import DataPath
from azureml.data.data_reference import DataReference
from azureml.data.dataset_type_definitions import PromoteHeadersBehavior
from azureml.data.dataset_error_handling import _validate_has_data
from azureml.data._dataprep_helper import dataprep
from azureml.data._loggerfactory import _LoggerFactory, track


_logger = None


def _get_logger():
    global _logger
    if _logger is not None:
        return _logger
    _logger = _LoggerFactory.get_logger(__name__)
    return _logger


class TabularDatasetFactory:
    """Contains methods to create tabular dataset for Azure Machine Learning service."""

    @staticmethod
    @track(_get_logger, activity_type=_PUBLIC_API)
    def from_parquet_files(path, validate=True, include_path=False, set_column_types=None):
        """Create a TabularDataset to represent tabular data in Parquet files.

        .. remarks::

            **from_parquet_files** creates an object of :class:`azureml.data.TabularDataset` class,
            which defines the operations to load data from Parquet files into tabular representation.

            For the data to be accessible by Azure Machine Learning service, the Parquet files specified by `path`
            must be located in :class:`azureml.core.Datastore` or behind public web urls.

            Column data types are read from data types saved in the Parquet files. Providing `set_column_types`
            will override the data type for the specified columns in the returned TabularDataset.

            .. code-block:: python

                from azureml.core import Dataset, Datastore

                # create tabular dataset from Parquet files in datastore
                datastore = Datastore.get(workspace, 'workspaceblobstore')
                datastore_path = [
                    (datastore, 'weather/2018/11.parquet'),
                    (datastore, 'weather/2018/12.parquet'),
                    (datastore, 'weather/2019/*.parquet')
                ]
                tabular = Dataset.Tabular.from_parquet_files(path=datastore_path)

                # create tabular dataset from Parquet files behind public web urls.
                web_path = [
                    'https://url/datafile1.parquet',
                    'https://url/datafile2.parquet'
                ]
                tabular = Dataset.Tabular.from_parquet_files(path=web_path)

                # use `set_column_types` to set column data types
                from azureml.data import DataType
                data_types = {
                    'ID': DataType.to_string(),
                    'Date': DataType.to_datetime('%d/%m/%Y %I:%M:%S %p'),
                    'Count': DataType.to_long(),
                    'Latitude': DataType.to_float(),
                    'Found': DataType.to_bool()
                }
                tabular = Dataset.Tabular.from_parquet_files(path=web_path, set_column_types=data_types)

        :param path: The path to locate the Parquet files.
        :type path: str, List[str], (azureml.core.Datastore, str) or List[(azureml.core.Datastore, str)]
        :param validate: Boolean to validate if data can be loaded from the returned dataset. Defaults to True.
            Validation requires that the data source is accessible from the current compute.
        :type validate: bool
        :param include_path: Boolean to keep path information as column in the dataset. Defaults to False.
            This is useful when reading multiple files, and want to know which file a particular record
            originated from, or to keep useful information in file path.
        :type include_path: bool
        :param set_column_types: A dictionary to set column data type, where key is column name and value is
            :class: azureml.data.DataType
        :type set_column_types: dict[str, TypeConversion]
        :return: Returns a :class:`azureml.data.TabularDataset` object.
        :rtype: azureml.data.TabularDataset
        """
        from azureml.data.tabular_dataset import TabularDataset

        dataflow = dataprep().read_parquet_file(_resolve_path(path),
                                                include_path=include_path,
                                                verify_exists=False)
        if validate or _is_inference_required(set_column_types):
            _validate_has_data(dataflow, 'Cannot load any data from the the specified path. ' +
                                         'Make sure the path is accessible and contains data.')
        dataflow = _set_column_types(dataflow, set_column_types)
        return TabularDataset._create(dataflow)

    @staticmethod
    @track(_get_logger, activity_type=_PUBLIC_API)
    def from_delimited_files(path, validate=True, include_path=False, infer_column_types=True, set_column_types=None,
                             separator=',', header=PromoteHeadersBehavior.ALL_FILES_HAVE_SAME_HEADERS):
        r"""Create a TabularDataset to represent tabular data in delimited files (e.g. CSV and TSV).

        .. remarks::

            **from_delimited_files** creates an object of :class:`azureml.data.TabularDataset` class,
            which defines the operations to load data from delimited files into tabular representation.

            For the data to be accessible by Azure Machine Learning service, the delimited files specified by `path`
            must be located in :class:`azureml.core.Datastore` or behind public web urls.

            Column data types are by default inferred from data in the delimited files. Providing `set_column_types`
            will override the data type for the specified columns in the returned TabularDataset.

            .. code-block:: python

                from azureml.core import Dataset, Datastore

                # create tabular dataset from delimited files in datastore
                datastore = Datastore.get(workspace, 'workspaceblobstore')
                datastore_path = [
                    (datastore, 'weather/2018/11.csv'),
                    (datastore, 'weather/2018/12.csv'),
                    (datastore, 'weather/2019/*.csv')
                ]
                tabular = Dataset.Tabular.from_delimited_files(path=datastore_path)

                # create tabular dataset from delimited files behind public web urls.
                web_path = [
                    'https://url/datafile1.tsv',
                    'https://url/datafile2.tsv'
                ]
                tabular = Dataset.Tabular.from_delimited_files(path=web_path, separator='\t')

                # use `set_column_types` to set column data types
                from azureml.data import DataType
                data_types = {
                    'ID': DataType.to_string(),
                    'Date': DataType.to_datetime('%d/%m/%Y %I:%M:%S %p'),
                    'Count': DataType.to_long(),
                    'Latitude': DataType.to_float(),
                    'Found': DataType.to_bool()
                }
                tabular = Dataset.Tabular.from_delimited_files(path=web_path, set_column_types=data_types)

        :param path: The path to locate the delimited files.
        :type path: str, List[str], (azureml.core.Datastore, str) or List[(azureml.core.Datastore, str)]
        :param validate: Boolean to validate if data can be loaded from the returned dataset. Defaults to True.
            Validation requires that the data source is accessible from the current compute.
        :type validate: bool
        :param include_path: Boolean to keep path information as column in the dataset. Defaults to False.
            This is useful when reading multiple files, and want to know which file a particular record
            originated from, or to keep useful information in file path.
        :type include_path: bool
        :param infer_column_types: Boolean to infer column data types. Defaults to True.
            Type inference requires that the data source is accessible from current compute.
        :type infer_column_types: bool
        :param set_column_types: A dictionary to set column data type, where key is column name and value is
            :class: azureml.data.DataType
        :type set_column_types: dict[str, TypeConversion]
        :param separator: The separator used to split columns.
        :type separator: str
        :param header: Controls how column headers are promoted when reading from files. Defaults to assume
            that all files have the same header.
        :type header: :class: azureml.data.dataset_type_definitions.PromoteHeadersBehavior.
        :return: Returns a :class:`azureml.data.TabularDataset` object.
        :rtype: azureml.data.TabularDataset
        """
        from azureml.data.tabular_dataset import TabularDataset

        dataflow = dataprep().read_csv(_resolve_path(path),
                                       verify_exists=False,
                                       include_path=include_path,
                                       infer_column_types=False,
                                       separator=separator,
                                       header=header)

        if validate or infer_column_types or _is_inference_required(set_column_types):
            _validate_has_data(dataflow, 'Cannot load any data from the the specified path. ' +
                                         'Make sure the path is accessible and contains data.')
        if infer_column_types:
            column_types_builder = dataflow.builders.set_column_types()
            column_types_builder.learn()
            if len(column_types_builder.ambiguous_date_columns) > 0:
                warnings.warn(('Ambiguous datetime formats inferred for columns {} are resolved as "month-day". ' +
                              'Desired format can be specified by `set_column_types`.')
                              .format(column_types_builder.ambiguous_date_columns))
                column_types_builder.ambiguous_date_conversions_keep_month_day()
            dataflow = column_types_builder.to_dataflow()

        dataflow = _set_column_types(dataflow, set_column_types)
        return TabularDataset._create(dataflow)

    @staticmethod
    @track(_get_logger, activity_type=_PUBLIC_API)
    def from_sql_query(query, validate=True, set_column_types=None):
        """Create a TabularDataset to represent tabular data in SQL databases.

        .. remarks::

            **from_sql_query** creates an object of :class:`azureml.data.TabularDataset` class,
            which defines the operations to load data from SQL databases into tabular representation.

            For the data to be accessible by Azure Machine Learning service, the SQL database specified by `query`
            must be located in :class:`azureml.core.Datastore` and the datastore type must be of a SQL kind.

            Column data types are read from data types in SQL query result. Providing `set_column_types`
            will override the data type for the specified columns in the returned TabularDataset.

            .. code-block:: python

                from azureml.core import Dataset, Datastore

                # create tabular dataset from a SQL database in datastore
                datastore = Datastore.get(workspace, 'mssql')
                tabular = Dataset.Tabular.from_sql_query((datastore, 'SELECT * FROM my_table'))
                df = tabular.to_pandas_dataframe()

                # use `set_column_types` to set column data types
                from azureml.data import DataType
                data_types = {
                    'ID': DataType.to_string(),
                    'Date': DataType.to_datetime('%d/%m/%Y %I:%M:%S %p'),
                    'Count': DataType.to_long(),
                    'Latitude': DataType.to_float(),
                    'Found': DataType.to_bool()
                }
                tabular = Dataset.Tabular.from_sql_query(path=web_path, set_column_types=data_types)

        :param query: A SQL-kind datastore and a query.
        :type query: tuple[azureml.core.Datastore, str], azureml.data.datapath.DataPath,
            or azureml.data.data_reference.DataReference
        :param validate: Boolean to validate if data can be loaded from the returned dataset. Defaults to True.
            Validation requires that the data source is accessible from the current compute.
        :type validate: bool
        :param set_column_types: A dictionary to set column data type, where key is column name and value is
            :class: azureml.data.DataType
        :type set_column_types: dict[str, TypeConversion]
        :return: Returns a :class:`azureml.data.TabularDataset` object.
        :rtype: azureml.data.TabularDataset
        """
        from azureml.data.tabular_dataset import TabularDataset

        dataflow = dataprep().read_sql(*_get_store_and_query(query))

        if validate or _is_inference_required(set_column_types):
            _validate_has_data(dataflow, 'Cannot load any data from the datastore using the SQL query "{}". '
                                         'Please make sure the datastore and query is correct.')
        dataflow = _set_column_types(dataflow, set_column_types)
        return TabularDataset._create(dataflow)


class DataType:
    """A class used to configure column data types for dataset created for Azure Machine Learning service."""

    @staticmethod
    def to_string():
        """Configure conversion towards string."""
        dt = DataType()
        dt._set_type_conversion(dataprep().TypeConverter(dataprep().FieldType.STRING))
        return dt

    @staticmethod
    def to_long():
        """Configure conversion towards 64-bit integer."""
        dt = DataType()
        dt._set_type_conversion(dataprep().TypeConverter(dataprep().FieldType.INTEGER))
        return dt

    @staticmethod
    def to_float():
        """Configure conversion towards 64-bit float."""
        dt = DataType()
        dt._set_type_conversion(dataprep().TypeConverter(dataprep().FieldType.DECIMAL))
        return dt

    @staticmethod
    def to_bool():
        """Configure conversion bool."""
        dt = DataType()
        dt._set_type_conversion(dataprep().TypeConverter(dataprep().FieldType.BOOLEAN))
        return dt

    @staticmethod
    def to_datetime(formats=None):
        """Configure conversion towards datetime.

        :param formats: Datetime formats to try for conversion. Like: `%d-%m-%Y`, `%Y-%m-%dT%H:%M:%S.%f`.
            Default to None. Format specifiers:
            * %Y: Year in 4 digit

            * %y: Year in 2 digit

            * %m: Month in digits

            * %b: Month represented by abbreviated name in 3 letters, like Aug

            * %B: Month represented by full name, like August

            * %d: Day in digits

            * %H: Hour represented by a 24-hour clock

            * %I: Hour represented by a 12-hour clock

            * %M: Minute in 2 digit

            * %S: Second in 2 digit

            * %f: Microsecond

            * %p: AM/PM designator

            * %z: timezone, like -0700

            Format specifiers will be inferred if not specified.
            Inference requires that the data source is accessible from current compute.
        :type formats: str or List[str]
        """
        dt = DataType()
        if not isinstance(formats, list):
            formats = [formats]
        if len(formats) == 0:
            formats = None
        dt._set_type_conversion(dataprep().DateTimeConverter(formats))
        return dt

    def _set_type_conversion(self, type_conversion):
        self._type_conversion = type_conversion


_set_column_types_type_error = TypeError(
    '`set_column_types` must be a dictionary where key is column name and value is :class: azureml.data.DataType')


def _is_inference_required(set_column_types):
    if set_column_types is None:
        return False
    try:
        for data_type in set_column_types.values():
            if isinstance(data_type._type_conversion, dataprep().DateTimeConverter) \
               and data_type._type_conversion.formats is None:
                return True
    except Exception:
        raise _set_column_types_type_error
    return False


def _set_column_types(dataflow, set_column_types):
    if set_column_types is None:
        return dataflow
    type_conversions = {}
    try:
        for column in set_column_types.keys():
            conversion = set_column_types[column]._type_conversion
            if not isinstance(column, str) or not isinstance(conversion, dataprep().TypeConverter):
                raise Exception()  # proper error message will be raised below
            type_conversions[column] = conversion
    except Exception:
        raise _set_column_types_type_error

    if len(type_conversions) == 0:
        return dataflow
    try:
        return dataflow.set_column_types(type_conversions)
    except Exception:
        raise RuntimeError('Cannot infer conversion format for datatime. Please provide the desired formats.')


def _resolve_path(paths):
    http_pattern = re.compile(r'^https?://', re.IGNORECASE)

    # TODO: remove below once https://msdata.visualstudio.com/Vienna/_git/AzureMlCli/pullrequest/239663?_a=overview
    # TODO: is released
    if isinstance(paths, str) and http_pattern.match(paths):
        if dataprep().__version__ < '1.1.11':
            raise Exception('Please install "azureml-dataprep>=1.1.11" to use "http://" or "https://" path.')
        return paths
    if not isinstance(paths, list):
        paths = [paths]
    if len(paths) == 0:
        raise ValueError('Paths cannot be empty list')

    if all([isinstance(p, str) for p in paths]):
        if any([not http_pattern.match(p) for p in paths]):
            raise ValueError('String value in path must be a url starting with "http://" or "https://".')
        if dataprep().__version__ < '1.1.11':
            raise Exception('Please install "azureml-dataprep>=1.1.11" to use "http://" or "https://".')
        return paths

    resolved = []
    for p in paths:
        if isinstance(p, DataPath) or isinstance(p, DataReference):
            resolved.append(p)
        elif _is_valid_path_tuple(p):
            resolved.append(DataPath(*p))
        else:
            raise TypeError('Invalid path found, path can only be a tuple of datastore and path string, DataPath, '
                            'or a DataReference. Found "{}"'.format(type(p).__name__))
    return resolved


def _get_store_and_query(query):
    if _is_valid_path_tuple(query):
        return query
    if isinstance(query, DataPath):
        return query._datastore, query.path_on_datastore
    if isinstance(query, DataReference):
        return query.datastore, query.path_on_datastore
    raise TypeError('Invalid argument value or type. Please refer to the documentation for accepted types.')


def _is_valid_path_tuple(path_tuple):
    if isinstance(path_tuple, tuple):
        if len(path_tuple) == 2 and isinstance(path_tuple[0], AbstractDatastore) and isinstance(path_tuple[1], str):
            return True
        raise ValueError(
            'Invalid tuple for path. Please make sure the tuple consists of a datastore and a path/SQL query')
    return False
