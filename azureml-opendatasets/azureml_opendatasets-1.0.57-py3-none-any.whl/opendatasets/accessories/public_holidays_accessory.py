# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Public holiday."""

from .country_or_region_time_public_data import CountryOrRegionTimePublicData
from ..enrichers.holiday_enricher import HolidayEnricher

from datetime import datetime
from dateutil import parser
from pandas import DataFrame as PdDataFrame
from pyspark.sql.functions import col
from pyspark.sql.dataframe import DataFrame as SparkDataFrame
from typing import Optional, List

from ..dataaccess._public_holidays_blob_info import PublicHolidaysBlobInfo
from ..dataaccess.blob_parquet_descriptor import BlobParquetDescriptor
from ..environ import SparkEnv, PandasEnv
from ..dataaccess.pandas_data_load_limit import PandasDataLoadLimitNone
from multimethods import multimethod


class PublicHolidaysAccessory(CountryOrRegionTimePublicData):
    """Public holiday accessory class."""

    default_start_date = parser.parse('2008-01-01')
    default_end_date = datetime.today()

    _blobInfo = PublicHolidaysBlobInfo()

    data = BlobParquetDescriptor(_blobInfo)

    def _prepare_cols(self):
        """Prepare columns that can be used to join with other data."""
        self.time_column_name = 'date'
        self.countrycode_column_name = 'countryRegionCode'
        self.country_or_region_column_name = 'countryOrRegion'

    def __init__(
            self,
            country_or_region: str = '',
            start_date: datetime = default_start_date,
            end_date: datetime = default_end_date,
            cols: Optional[List[str]] = None,
            enable_telemetry: bool = True):
        """
        Initialize filtering fields.

        :param country_or_region: country or region you'd like to query against.
        :type country_or_region: str
        :param start_date: start date you'd like to query inclusively.
        :type start_date: datetime
        :param end_date: end date you'd like to query inclusively.
        :type end_date: datetime
        :param cols: a list of column names you'd like to retrieve. None will get all columns.
        :type cols: Optional[List[str]]
        :param enable_telemetry: whether to send telemetry
        :type enable_telemetry: bool
        """
        self.dataset = None
        self._registry_id = self._blobInfo.registry_id
        self.path = self._blobInfo.get_data_wasbs_path()
        self._prepare_cols()

        if country_or_region is None:
            raise ValueError('Unsupported country or region:' + country_or_region)
        self.country_or_region = country_or_region
        self.start_date = start_date\
            if (self.default_start_date < start_date)\
            else self.default_start_date
        self.end_date = end_date\
            if (self.default_end_date > end_date)\
            else self.default_end_date
        super(PublicHolidaysAccessory, self).__init__(cols=cols, enable_telemetry=enable_telemetry)
        if enable_telemetry:
            self.log_properties['CountryOrRegion'] = self.country_or_region
            self.log_properties['StartDate'] = self.start_date
            self.log_properties['EndDate'] = self.end_date
            self.log_properties['Path'] = self.path

    def update_dataset(self, ds, enable_telemetry: bool = True):
        """Update dataset."""
        self.dataset = ds
        if enable_telemetry:
            self.log_properties['from_dataset'] = True

    @multimethod(SparkEnv, SparkDataFrame)
    def _filter_country_region(self, env, data):
        """Filter country or region."""
        if len(self.country_or_region) > 0:
            data = data.where((col(self.countrycode_column_name) == self.country_or_region) | (
                col(self.country_or_region_column_name) == self.country_or_region))
        return data

    @multimethod(PandasEnv, PdDataFrame)
    def _filter_country_region(self, env, data):
        """Filter country or region."""
        if len(self.country_or_region) > 0:
            data = data[(data[self.countrycode_column_name] == self.country_or_region) & (
                data[self.countrycode_column_name] == self.country_or_region)]
        return data

    @multimethod(SparkEnv, datetime, datetime)
    def filter(self, env, min_date, max_date):
        """Filter time.

        :param min_date: min date
        :param max_date: max date

        :return: filtered data frame.
        """
        self.data = self.data.na.drop(how='all', subset=self.cols).na.drop(how='any', subset=[self.time_column_name])
        self.data = self._filter_country_region(env, self.data)

        ds = super(PublicHolidaysAccessory, self).filter(env, min_date, max_date)
        ds = self._filter_country_region(env, ds)
        return ds.select(*self.selected_columns)

    @multimethod(PandasEnv, datetime, datetime)
    def filter(self, env, min_date, max_date):
        """Filter time.

        :param min_date: min date
        :param max_date: max date

        :return: filtered data frame.
        """
        ds = super(PublicHolidaysAccessory, self).filter(env, min_date, max_date)
        ds = ds.dropna(how='all', axis=0, subset=self.cols).dropna(
            how='any', axis=0, subset=[self.time_column_name])
        ds = self._filter_country_region(env, ds)

        return ds[self.selected_columns]

    def _get_enricher(self, activity_logger):
        """Get enricher object."""
        return HolidayEnricher(self, enable_telemetry=self.enable_telemetry)

    def _get_mandatory_columns(self):
        """
        Get mandatory columns to select.

        :return: a list of column names.
        :rtype: list
        """
        return [self.time_column_name, self.country_or_region_column_name, self.countrycode_column_name]

    def get_pandas_limit(self):
        """Get instance of pandas data load limit class."""
        return PandasDataLoadLimitNone()

    def _to_spark_dataframe(self, activity_logger):
        """To spark dataframe.

        :param activity_logger: activity logger

        :return: SPARK dataframe
        """
        descriptor = BlobParquetDescriptor(self._blobInfo)
        ds = descriptor.get_spark_dataframe(self)
        ds = self._filter_country_region(SparkEnv(), ds)
        return ds

    def _to_pandas_dataframe(self, activity_logger):
        """
        Get pandas dataframe.

        :param activity_logger: activity logger

        :return: Pandas dataframe based on its own filters.
        :rtype: pandas.DataFrame
        """
        descriptor = BlobParquetDescriptor(self._blobInfo)
        ds = descriptor.get_pandas_dataframe(self)
        ds = self._filter_country_region(PandasEnv(), ds)
        return ds
