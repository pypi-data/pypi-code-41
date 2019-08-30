""" Module for type guessing """
import pandas as pd
from pandas.api.types import is_float_dtype, is_numeric_dtype

import raven_preprocess.col_info_constants as col_const
from raven_preprocess.column_info import ColumnInfo
from raven_preprocess.basic_utils.basic_err_check import BasicErrCheck


class TypeGuessUtil(BasicErrCheck):
    """Check variable types of a dataframe"""
    def __init__(self, col_series, col_info):
        """Init with a pandas dataframe"""
        assert col_series is not None, "dataframe can't be None"

        self.col_series = col_series
        self.col_info = col_info
        self.binary = False
        # # final outout returned
        self.check_types()

    def check_types(self):
        """check the types of the dataframe"""
        # assert self.colnames, 'self.colnames must have values'
        # number of missing entries
        #
        self.col_info.invalid = int(self.col_series.isnull().sum())

        # number of valid entries
        #
        self.col_info.valid = int(self.col_series.count())

        # set time , what exactly we want to do with this
        #
        self.col_info.time_val = self.check_time(self.col_series)

        # Drop nulls...
        self.col_series.dropna(inplace=True)

        uniques = self.col_series.unique()

        binary = self.check_binary(len(uniques))

        # set up binary values..
        if binary:
            self.col_info.binary = col_const.BINARY_YES
        else:
            self.col_info.binary = col_const.BINARY_NO
        if self.is_not_numeric(self.col_series) or self.is_logical(self.col_series):

            self.col_info.numchar_val = col_const.NUMCHAR_CHARACTER
            self.col_info.default_interval = col_const.INTERVAL_DISCRETE
            self.col_info.nature = col_const.NATURE_NOMINAL

        else:

            try:
                series_info = self.col_series.astype('int')
            except ValueError as err_obj:
                user_msg = ('Type guess error when converting'
                            ' to int: %s') % err_obj
                self.add_err_msg(user_msg)
                return

            if any(series_info.isnull()):
                # CANNOT REACH HERE B/C NULLS ARE DROPPED!
                #
                self.col_info.numchar_val = col_const.NUMCHAR_CHARACTER
                self.col_info.nature = col_const.NATURE_NOMINAL
                self.col_info.default_interval = col_const.INTERVAL_DISCRETE
            else:
                self.col_info.numchar_val = col_const.NUMCHAR_NUMERIC

                if is_float_dtype(series_info):
                    self.col_info.default_interval = col_const.INTERVAL_CONTINUOUS
                    self.col_info.nature = self.check_nature(series_info, True)

                else:
                    self.col_info.default_interval = col_const.INTERVAL_DISCRETE
                    self.col_info.nature = self.check_nature(series_info, False)




    @staticmethod
    def is_not_numeric(var_series):
        """Check if pandas Series is a numeric"""
        assert isinstance(var_series, pd.Series), \
            "var_series must be a pandas.Series. Found type: (%s)" % type(var_series)

        var_series.dropna(inplace=True)
        if var_series.size == 0:
            # print("character")
            return True
        elif var_series.dtype == 'bool':
            return True

        if is_numeric_dtype(var_series):
            return False
        else:
            return True

    @staticmethod
    def is_logical(var_series):
        """Check if pandas Series contains boolean values"""
        assert isinstance(var_series, pd.Series), \
            "var_series must be a pandas.Series. Found type: (%s)" % type(var_series)

        var_series.dropna(inplace=True)

        # Check the dtype
        #    "bool" - True, clearly logical
        #    "object" - possibly logical that had contained np.Nan
        #    ~anything else~ - False
        #
        if var_series.dtype == 'bool':
            return True
        elif var_series.dtype != 'object':
            return False

        # It's an object.  Check if all the values
        #   either True or False
        #
        total = var_series.size
        total_cnt = 0
        for val, cnt in var_series.value_counts().iteritems():
            if val is True or val is False:
                total_cnt = total_cnt + cnt

        if total_cnt == total:
            # This is a boolean -- everything was either True or False
            #
            return True

        return False

    @staticmethod
    def check_nature(data_series, continuous_check):
        """Check the nature of the Series"""
        if continuous_check:
            if data_series.between(0, 1).all():
                return col_const.NATURE_PERCENT
            elif data_series.between(0, 100).all() and min(data_series) < 15 and max(data_series) > 85:
                return col_const.NATURE_PERCENT
            else:
                return col_const.NATURE_RATIO

        else:
            return col_const.NATURE_ORDINAL

    @staticmethod
    def check_time(var_series):
        """Unimplemented"""
        assert isinstance(var_series, pd.Series), \
            "var_series must be a pandas.Series. Found type: (%s)" % type(var_series)

        return col_const.UNKNOWN

    @staticmethod
    def check_binary(unique_size):
        """ check if the series is binary or not """
        if unique_size is 2:
            return True
        else:
            return False
