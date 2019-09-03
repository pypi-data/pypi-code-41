# Todo :
#  - Dispatch on type for type selection with @singladispatch

import ast
import io
import re
import unicodedata as ud
from os import remove
from string import digits
from tempfile import mkstemp

import joblib
import numpy as np
import pandas as pd
from requests import put
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from .config import NOT_PROCESSORS_METHOD, PROCESSING_PROCESSORS, FILTER_ACTIONS, FILTER_NORM_MODES, COMMON_PROCESSORS
from .dataframe_statistics import DataFrameStatistics
from .exceptions import DataFrameError, ProcessorError, ColumnNotFound, ConversionError
from .s3 import s3_client
from .sklearn_estimators import MissingValuesHandler, ScalarNormalizer, Smoother


class DataFrameManipulator:
    """Encapsulate input df and config, apply transformation to data_set based on column name"""

    def __init__(self, in_data=None, mode='use', logger=print, s3_bucket_name=None, aws_access_key_id=None,
                 aws_secret_access_key=None,
                 aws_region_name=None):
        try:
            assert isinstance(in_data, pd.DataFrame) or in_data is None
        except AssertionError:
            raise DataFrameError('ERROR, expected a pandas DataFrame as input.')

        self._df = in_data
        self.mode = mode  # either build, build_save, use
        self.original = in_data
        self._steps = []
        self._error = []
        self.success = False
        self.logger = logger
        self.s3_bucket_name = s3_bucket_name
        self.s3_client = s3_client(aws_access_key_id, aws_secret_access_key, aws_region_name)

    def __str__(self):
        count = []
        for step in self.steps:
            elements = len(self.steps[step])
            count.append(f'{step} : {elements}')
        count_string = '\n' + '\n'.join(count) + '\n'
        buf = io.StringIO()
        self.df.info(buf=buf)
        info = buf.getvalue()
        string = f'This is a DataFrame manipulator that has : \n' \
                 f'DataFrame Info : \n {info}' \
                 f'\nSteps count: {count_string}'
        return string

    def __repr__(self):
        return f'DataFrameManipulator(data_frame : {self.df}, steps : {self.steps})'

    @property
    def steps(self):
        return self._steps

    @property
    def errors(self):
        return self._error

    @steps.setter
    def steps(self, value):
        self._steps = value.copy()
        self.run_steps()

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, value):
        if not isinstance(value, pd.DataFrame):
            raise DataFrameError(
                'ERROR, expected a pandas DataFrame as input.')
        self._df = value.copy()
        self.original = value.copy()

    def run_steps(self):
        """save operations in steps as dictionaries of steps and apply the method to the df"""
        self._df = self.original.copy()
        for i, step in enumerate(self._steps):
            processor, activated, id_ = step['processor'], step['activated'], step.get('_id', i)
            s3_key = step.get('s3_key', None)
            params = step.get('params', {})
            if s3_key:
                params['s3_key'] = s3_key
            if activated:
                try:
                    method = f'_{processor}'
                    kwargs = self._verify_params(params)
                    getattr(self, method)(**kwargs)
                    mess = 'No error for this step'
                except TypeError as e:
                    e = str(e)
                    table = {ord(digit): None for digit in digits}
                    e = e.translate(table)
                    missing = re.findall(r"'(.*?)'", e)
                    missing = [e.replace('_', ' ').strip().capitalize() for e in missing]
                    missing = ', '.join(missing)
                    mess = f'PARAMETERS ERROR, When applying the step # {i + 1}, missing parameters : {missing}' \
                           f' , this is the error {e}'
                except ProcessorError as e:
                    mess = f'PROCESS ERROR, when applying the step # {i + 1} : {e}'
                except ColumnNotFound as e:
                    mess = f'COLUMN ERROR, when applying the step # {i + 1} : {e}'
                except AssertionError as e:
                    mess = f'ERROR, when applying the step # {i + 1} : {e}'
                except Exception as e:
                    mess = f'SPECIFIC ERROR, when applying the step # {i + 1} : {e.__class__.__name__} , {e}'
                else:
                    self.success = True
                if not self.success:
                    error = {
                        'message': mess,
                        'step_id': id_
                    }
                    self._error.append(error)

    @classmethod
    def processors_list(cls):
        processors = {}
        for function in dir(cls):
            if function not in NOT_PROCESSORS_METHOD:
                method = getattr(cls, function)
                params = ast.literal_eval(method.__doc__)
                processors[function[1:]] = params
        processors_list = {
            'processors': processors,
            'processing': PROCESSING_PROCESSORS,
            'commons': COMMON_PROCESSORS,
        }
        return processors_list

    def statistics(self, column_name):
        stats = DataFrameStatistics(self._df)
        statistics = stats.run(column_name)
        return statistics

    def _verify_params(self, kwargs):

        cols = kwargs['columns_to_process']
        cols = self._check_column_existence(cols)
        kwargs['columns_to_process'] = cols
        return kwargs

    def _check_column_existence(self, cols):
        """Check if columns exist in the DataFrame and, convert to list if not."""
        if not isinstance(cols, list):
            cols = [cols]
        for col in cols:
            try:
                assert col in self._df.columns
            except AssertionError:
                raise ColumnNotFound(
                    f'{col} is not found in the DataFrame')
        return cols

    # -------------------------------------  PROCESSOR METHODS   ---------------------------------------- #

    def _delete(self, columns_to_process, **kwargs):
        """{
            "name": "Delete column",
            "params": {
                'columns_to_process': {
                    'label': 'Column(s) to process',
                    'type': 'str',
                    'default': [],
                    'input-type' : 'drop-down-list',
                    'optional': False,
                    'description': 'Column name to process.'
                },
            },
            "description": "Remove column from the DataFrame"
        }"""
        try:
            self._df.drop(columns_to_process, axis=1, inplace=True)
        except KeyError as e:
            raise ProcessorError(f'cannot delete column not found {e}')

    def _keep_only(self, columns_to_process, **kwargs):
        """{
            "name" : "Keep these columns only",
            "params": {
                'columns_to_process': {
                    'label': 'Column(s) to process',
                    'type': 'str',
                    'default': [],
                    'input-type' : 'drop-down-list',
                    'optional': False,
                    'description': 'Column name to process.'
                },
            },
            "description" : "Keep these columns only"
        }"""
        try:
            self._df = self._df[columns_to_process]
        except KeyError as e:
            raise ProcessorError(f'cannot keep these columns not found')

    def _rename(self, columns_to_process, new_name, **kwargs):
        """{
            "name" : "Rename column",
            "params" : {
                'columns_to_process': {
                        'label': 'Column(s) to process',
                        'type': 'str',
                        'default': '',
                        'input-type': 'drop-down',
                        'optional': False,
                        'description': 'Column name to process.'
                    },
                'new_name' : {
                    'label' : 'New name for this column',
                    'type' : 'str',
                    'default' : "new_name",
                    'input-type' : 'text',
                    'optional':False,
                    'description' : 'Insert the new name for the column'
                }
            },
            "description" : "Rename a column"
        }"""
        column_to_process = columns_to_process[0]  # TODO remove [0] once drop down fixed
        if new_name in self._df.columns:
            raise ProcessorError(f'cannot use {new_name}, this name already used in the Dataframe\'s columns.')
        try:
            self._df.rename(index=str, columns={column_to_process: new_name}, inplace=True)
        except Exception as e:
            raise ProcessorError(f'cannot use this new name for this column choose an other one. {e}')

    def _move_to(self, columns_to_process, position, index=0, **kwargs):
        """{
            "name" : "Move column to",
            "params" : {
                'columns_to_process': {
                        'label': 'Column(s) to process',
                        'type': 'str',
                        'default': '',
                        'input-type': 'drop-down',
                        'optional': False,
                        'description': 'Column name to process.'
                    },
                'position' : {
                        'label' : 'Move column(s) to',
                        'type' : 'str',
                        'default' : "end",
                        "choices" : ["beginning","end", "index"],
                        'input-type' : 'drop-down',
                        'optional' : False,
                        'description' : 'The position where to move the column to.'
                },
                'index' : {
                        'label' : 'New index',
                        'type' : 'int',
                        'default' : 0,
                        'input-type':'text',
                        'visibility_cond': [{
                            'param' : 'position',
                            'value' : 'index'
                        }],
                        'optional' : False,
                        'description' : 'The index of the position.'
                }
            },
            "description" : "Move this column to a specific position"
        }"""
        df_cols = list(self._df.columns)
        col = columns_to_process[0]  # TODO remove  [0] after drop-down fixed
        _ = {
            'beginning': 0,
            'end': len(df_cols)
        }
        try:
            index = _[position] if position != "index" else index
            df_cols.remove(col)
            df_cols.insert(index, col)
            self._df = self._df[df_cols]
        except KeyError:
            raise ProcessorError(
                f'position must be "begening" , "end"  or integer index ')

    def _move_after(self, columns_to_process, previous_column, **kwargs):
        """{
                "name" : "Move column after",
                "params": {
                    'columns_to_process': {
                        'label': 'Column(s) to process',
                        'type': 'str',
                        'default': '',
                        'input-type': 'drop-down',
                        'optional': False,
                        'description': 'Column name to process.'
                    },
                    'previous_column' : {
                            'label' : 'Move after',
                            'type' : 'str',
                            'default' : '',
                            'input-type' : 'drop-down',
                            'optional' : False,
                            'description' : 'Column where to move the column after'
                    }
                },
                'description' : 'Move a column after an other one.'
        }"""
        col = columns_to_process[0]  # TODO remove  [0] after drop-down fixed
        if col == previous_column:
            raise ProcessorError(
                'the column to be moved should not be the same as the reference column')

        cols = list(self._df.columns)
        try:
            cols.remove(col)
            index = cols.index(previous_column) + 1
            cols.insert(index, col)
            self._df = self._df[cols]
        except ValueError:
            if col in cols:
                raise ProcessorError('"' + str(
                    previous_column) + '" not found in DataFrame columns')
            raise ProcessorError(
                '"' + str(col) + '" not found in DataFrame columns')

    def _lowercase(self, columns_to_process, **kwargs):
        """{
            "name" : "To lowercase",
            "params": {
                'columns_to_process': {
                    'label': 'Column(s) to process',
                    'type': 'str',
                    'default': [],
                    'input-type' : 'drop-down-list',
                    'optional': False,
                    'description': 'Column name to process.'
                },
            },
            "description" : "This processor is used to convert only string to lowercase."
        }"""
        for col in columns_to_process:
            try:
                self._df[col] = self._df[col].str.lower()
            except Exception:
                raise ProcessorError(
                    f'cannot convert "{col}" to lowercase. Only string columns can be converted to lowercase.')

    def _uppercase(self, columns_to_process, **kwargs):
        """{
            "name" : "To uppercase",
            "params": {
                'columns_to_process': {
                    'label': 'Column(s) to process',
                    'type': 'str',
                    'default': [],
                    'input-type' : 'drop-down-list',
                    'optional': False,
                    'description': 'Column name to process.'
                },
            },
            "description" : "This processor is used to convert only string to lowercase."
        }"""
        for col in columns_to_process:
            try:
                self._df[col] = self._df[col].str.upper()
            except Exception:
                raise ProcessorError(
                    f'cannot convert "{col}" to uppercase. Only string columns can be converted to uppercase.')

    def _capitalise(self, columns_to_process, **kwargs):
        """{
            "name" : "Capitalise column",
            "params": {
                'columns_to_process': {
                    'label': 'Column(s) to process',
                    'type': 'str',
                    'default': [],
                    'input-type' : 'drop-down-list',
                    'optional': False,
                    'description': 'Column name to process.'
                },
            },
            "description" : "This processor is used to convert only string to lowercase."

        }"""
        for col in columns_to_process:
            try:
                self._df[col] = self._df[col].str.capitalize()
            except Exception:
                raise ProcessorError(f'cannot capitalize {col}. Only string columns can be capitalized.')

    def _filter_rows_on_value(self, columns_to_process, action, value, match_mode=None, norm_mode=None, **kwargs):
        """{
            "name" : "Filter rows according to value",
            "params": {
                'columns_to_process': {
                    'label': 'Column(s) to process',
                    'type': 'str',
                    'default': [],
                    'input-type' : 'drop-down-list',
                    'optional': False,
                    'description': 'Column name to process.'
                },
                'action' : {
                        'label' : 'Action',
                        'type' : 'str',
                        'default' : "Remove rows",
                        "choices" : ["Remove rows", "Keep these rows only"],
                        'input-type' : 'drop-down',
                        "optional": False,
                        "description": "Action to perform on matching rows."
                },
                'value' : {
                        'label' : 'Value',
                        'type' : 'str',
                        'default' : '0',
                        'input-type':'text',
                        'optional' : False,
                        'description' : 'Value on these columns to process'
                },
                'match_mode':{
                        'label' : 'Matching mode',
                        'type' : 'str',
                        'default' : "Complete",
                        "choices" : ['Complete', 'Substring'],
                        'input-type' : 'drop-down',
                        'optional' : False,
                        'description' : 'Either matching with complete string or substring search.'
                },
                'norm_mode':{
                        'label' : 'Text norm mode',
                        'type' : 'str',
                        'default' : "Exact",
                        "choices" : ['Exact', 'Ignore Case', 'Normalize'],
                        'input-type' : 'drop-down',
                        'optional': False,
                        'description' : 'Normalisation mode'
                }
            },
            "description" : "This processor is used to filter the data rows according to a value."

        }"""

        acts = FILTER_ACTIONS
        functions = [self._filter_value_remove_rows,
                     self._filter_value_keep_rows]
        func = dict(zip(acts, functions)).get(action, functions[0])
        for col in columns_to_process:
            try:
                value = self._convert_value_to_col_type(col, value)
            except ConversionError as e:
                raise ProcessorError(f'{e}')
            for index, row in self._df.iterrows():
                df_value = row[col]
                val, df_val = self._apply_mode(value, df_value, norm_mode)
                func(index, val, df_val, match_mode)

    def _filter_rows_on_numerical_range(self, columns_to_process, action, mini, maxi, **kwargs):
        """{
            "name" : "Filter numerical rows in range",
            "params": {
                 'columns_to_process': {
                    'label': 'Column(s) to process',
                    'type': 'str',
                    'default': [],
                    'input-type' : 'drop-down-list',
                    'optional': False,
                    'description': 'Column name to process.'
                },
                'action' : {
                        'label' : 'Action',
                        'type' : 'str',
                        'default' : "Remove rows",
                        "choices" : ["Remove rows", "Keep these rows only"],
                        'input-type' : 'drop-down'
                    },
                'mini' : {
                        'label' : 'Minimum value',
                        'type' : 'float',
                        'default': 0.0,
                        'input-type' : 'text',
                        'optional' : False,
                        'description':'Minimum value of the range.'

                    },
                'maxi' : {
                        'label' : 'Maximum value',
                        'type' : 'float',
                        'default' :  10.0,
                        'input-type' : 'text',
                        'optional' : False,
                        'description':'Maximum value of the range.'
                    }
            },
            "description" : "Filter rows in respect of a numerical range."
        }"""
        for col in columns_to_process:
            type_map = {
                'int64': True,
                'float64': True,
                'int32': True,
                'float32': True,
                'object': False,
                'bool': False,
                'datetime64[ns]': False,
                'timedelta[ns]': False,
                'category': False
            }
            try:
                assert type_map[str(self._df[col].dtype)]
            except AssertionError:
                raise ProcessorError(
                    'column must be of numerical type, in order to filter to filter with numerical range.')
            actions = FILTER_ACTIONS
            condition_maxi = self._df[col] <= eval(str(maxi))
            condition_mini = self._df[col] >= eval(str(mini))

            actors = [self._df[col][~ (condition_maxi & condition_mini)],
                      self._df[col][condition_maxi & condition_mini]]
            self._df[col] = dict(zip(actions, actors)).get(action, actors[0])
            self._df = self._df[np.isfinite(self._df[col])]

    def _set_as_index(self, columns_to_process, **kwargs):
        """{
               "name" : "Set as index",
               "params": {
                    'columns_to_process': {
                        'label': 'Column(s) to process',
                        'type': 'str',
                        'default': '',
                        'input-type': 'drop-down',
                        'optional': False,
                        'description': 'Column name to process.'
                    },
                },
               "description" : "This will make the first column selected as the index for the DataFrame"
        }"""
        column_to_process = columns_to_process[0]  # TODO remove  [0] after drop-down fixed
        if self.df[column_to_process].isnull().any():
            raise ProcessorError(f'cannot use this column as index, it contains missing values.')
        try:
            self._df = self._df.set_index(column_to_process)
        except Exception as e:
            raise ProcessorError(f'cannot set this column as index {e}')

    def _reset_index(self, columns_to_process, **kwargs):
        """{
                   "name" : "Reset Dataframe index",
                   'columns_to_process': {
                        'label': 'Column(s) to process',
                        'type': 'str',
                        'default': '',
                        'input-type': 'drop-down',
                        'optional': False,
                        'description': 'Column name to process.'
                },
                   "description" : "Reset the column of the DataFrame."

        }"""
        try:
            self._df = self._df.reset_index()
            self._df.drop(columns=['index'], inplace=True)
        except Exception as e:
            raise ProcessorError(f'unable to reset the index {e}')

    def _convert_index_to_date_time(self, columns_to_process, **kwargs):
        """{
               "name" : "Convert to datetime",
               "params": {
                    'columns_to_process': {
                        'label': 'Column(s) to process',
                        'type': 'str',
                        'default': [],
                        'input-type' : 'drop-down-list',
                        'optional': False,
                        'description': 'Column name to process.'
                    },
                },
               "description" : "Convert the frist column selected as "
        }"""
        for col in columns_to_process:
            try:
                self._df[col] = pd.to_datetime(self._df[col])
            except ValueError:
                raise ProcessorError(f'cannot convert {col} to date time')

    def _change_type(self, columns_to_process, new_type, **kwargs):
        """{
                "name" : "Change column type",
                "params": {
                    'columns_to_process': {
                        'label': 'Column(s) to process',
                        'type': 'str',
                        'default': [],
                        'input-type' : 'drop-down-list',
                        'optional': False,
                        'description': 'Column name to process.'
                    },
                    'new_type' : {
                        'label' : 'Data type',
                        'type' : 'str',
                        'default': 'String',
                        'choices' : ['string','integer','float', 'bool', 'datetime', 'time_delta','category'],
                        'input-type' : 'drop-down',
                        'optional' : False,
                        'description' : 'Data target type.'
                    }
                },
                "description" : "Change the type of the column."

        }"""
        type_map = {
            'string': 'object',
            'integer': 'int64',
            'float': 'float64',
            'bool': 'bool',
            'datetime': 'datetime64[ns]',
            'category': 'category'
        }
        for col in columns_to_process:
            try:
                type_ = type_map.get(new_type, 'object')
                if type_ == 'float64':
                    try:
                        self._df[col] = self._df.apply(lambda x: x[col].replace(',', '.'), axis=1)
                    except TypeError:
                        pass
                if type_ == 'datetime64[ns]':
                    self._df[col] = pd.to_datetime(self._df[col])
                else:
                    self._df[col] = self._df[col].astype(type_)
            except ValueError:
                raise ProcessorError(
                    f'make sure conversion is valid, for example literal values cannot be '
                    f'converted to integers, also check if there are missing values in your data')

    def _missing_values(self, columns_to_process, missing_values=np.nan, value_for_missing_value=None, axis='0',
                        how='any', strategy='drop', fill_value=None, s3_key='', **kwargs):
        """{
                "name" : "Missing values operations",
                "to_save" : True,
                "params": {
                    'columns_to_process': {
                        'label': 'Column(s) to process',
                        'type': 'str',
                        'default': [],
                        'input-type' : 'drop-down-list',
                        'optional': False,
                        'description': 'Column name to process.'
                    },
                    'missing_values': {
                        'label': 'Missing values',
                        'type': 'str',
                        'default': 'NaN',
                        'choices': ['NaN', 'None', 'String', 'Numerical'],
                        'input-type': 'drop-down',
                        'optional': True,
                        'description': 'The placeholder for the missing values. All'
                                       ' occurrences of missing_values will be imputed.'
                    },
                    'value_for_missing_value': {
                        'label': 'String or numerical for missing value',
                        'type': 'float',
                        'default': '<missing>',
                        'input-type': 'text',
                        'optional': False,
                        'visibility_cond': [
                            [{
                                'param': 'missing_values',
                                'value': 'String'
                            }],
                            [{
                                'param': 'missing_values',
                                'value': 'Numerical'
                            }]
                        ],
                        'description': 'If a string or Numerical, placeholder chosen as missing values.'
                    },
                    'how':{
                        'label':'How to drop ?',
                        'type' : 'str',
                        'default' : 'any',
                        'choices' : ['any','all','columns'],
                        'input-type' : 'drop-down',
                        'optional' : False,
                        'visibility_cond' : [[
                            {
                                'param' : 'strategy',
                                'value' : 'drop',
                            }
                        ],[]],
                        'description' : 'If using the drop strategy, with which method to drop the missing values.'
                    },
                    'strategy': {
                        'label': 'Strategy',
                        'type': 'str',
                        'default': 'drop',
                        'choices': ['mean', 'median', 'constant', 'drop'],
                        'input-type': 'drop-down',
                        'optional': True,
                        'description': 'Strategy for handling missing values in the DataSet.'
                    },
                    'axis': {  # TODO Convert type to int if numerical
                        'label': 'Axis for dropping',
                        'type': 'str',
                        'default': '0',
                        'input-type': 'text',
                        'optional': True,
                        'visibility_cond': [[
                            {
                                'param': 'strategy',
                                'value': 'drop'
                            }
                        ], []],
                        'description': 'Axis along which to operate the drop.'
                    },
                    'fill_value': {
                        'label': 'Fill value',
                        'type': 'str',
                        'default': '0',
                        'input-type': 'text',
                        'optional': False,
                        'visibility_cond': [[
                            {
                                'param': 'strategy',
                                'value': 'constant'
                            }
                        ], []],
                        'description': 'Fill value if using a constant strategy.'
                    }
                },
                "description" : "Dealing with missing values in your dataframe."
        }"""
        how = {
            'any': 'any',
            'all': 'all',
            'columns': columns_to_process
        }.get(how, columns_to_process)

        if missing_values == 'String' or missing_values == 'Numerical':
            assert len(columns_to_process) == 1, 'only a column may be targeted if selecting a constant strategy.'
            value_for_missing_value = self._convert_value_to_col_type(columns_to_process[0], value_for_missing_value)

        if strategy == 'drop':
            columns_to_process = how
        elif strategy == 'constant':
            assert len(columns_to_process) == 1, 'only a column may be targeted if selecting a constant strategy.'
            fill_value = self._convert_value_to_col_type(columns_to_process[0], fill_value)
        axis = {
            '0': 0,
            '1': 1,
            'index': 0,
            'columns': 1
        }.get(axis, 0)

        missing_values = {
            'NaN': np.nan,
            'None': None,
            'String': value_for_missing_value,
            'Numerical': value_for_missing_value
        }.get(missing_values, np.nan)

        try:
            handler = MissingValuesHandler(columns=columns_to_process, missing_values=missing_values, strategy=strategy,
                                           axis=axis, fill_value=fill_value)
        except Exception as e:
            raise ProcessorError(f'Something went wrong when creating the missing values handler. {e}')

        try:
            self._df = self._apply_model_step(handler, self._df, s3_key=s3_key)
        except Exception as e:
            raise ProcessorError(
                f'cannot perform missing value handling.  {e}')

    # # --------------------------------------  PROCESSING FUNCTIONS  ----------------------------------------- #

    def _index(self, columns_to_process, _5start_date='2000-01-01 00:00:00', _6end_date='2020-01-01 00:00:00',
               _7period=0, _4new_name='time_index', _8frequency='D', _9fill_value='0',
               _1action='Convert index column to DateTime', _2index_type='Date Time index',
               _3element_to_adapt='Adapt index date', **kwargs):
        """{
            "name": "Index the DataFrame as Time series.",
            "params": {
                 'columns_to_process': {
                    'label': 'Column(s) to process',
                    'type': 'str',
                    'default': '',
                    'input-type': 'drop-down',
                    'optional': False,
                    'description': 'Column name to process.'
                },
                '_1action': {
                    'label': 'Action',
                    'type': 'str',
                    'default': 'Create index column',
                    'choices': ['Create index column',
                                'Convert index column to DateTime',
                                'Reindex the column'],
                    'input-type': 'drop-down',
                    'optional ': False,
                    'description': 'Action to perform with the dataframe.'
                },
                '_2index_type': {
                    'label': 'Type',
                    'type': 'str',
                    'default': 'Date Time index',
                    'choices': ['Date Time index',
                                'Period Time index'],
                    'input-type': 'drop-down',

                    'optional': False,
                    'description': 'The type of the time index to use'
                },
                '_3element_to_adapt': {
                    'label': 'Element to adapt',
                    'type': 'str',
                    'default': 'Adapt index date',
                    'choices': ['Adapt index date',
                                'Adapt Dataframe length',
                                'Adapt sampling frequency (Ignore frequency)'],
                    'input-type': 'drop-down',
                    'optional': False,
                    'description': 'Which element to adapt (Index and Dataframe length mismatch)'
                },
                '_4new_name': {
                    'label': 'Column name',
                    'type': 'str',
                    'default': 'time_index',
                    'input-type': 'text',
                    'optional': False,
                    'visibility_cond': [[
                        {
                            'param': '_1action',
                            'value': 'Create index column'
                        }
                    ], []],
                    'description': 'New column name to use as the index'
                },
                '_5start_date': {
                    'label': 'Start Date Time',
                    'type': 'str',
                    'default': '2000-01-01 00:00:00',
                    'input-type': 'text',
                    'optional': False,
                    'visibility_cond': [[
                        {
                            'param': '_1action',
                            'value': 'Create index column'
                        }
                    ], []],
                    'description': 'Start Date time for the range of the index , in the format (yy-MM-dd hh:mm:ss)'
                },
                '_6end_date': {
                    'label': 'End Date time',
                    'type': 'str',
                    'default': '2020-01-01 00:00:00',
                    'input-type': 'text',
                    'optional': False,
                    'visibility_cond': [[
                        {
                            'param': '_1action',
                            'value': 'Create index column'
                        }
                    ], []],
                    'description': 'End date for the range of the index. In the format (yy-MM-dd hh:mm:ss)'
                },
                '_7period': {
                    'label': 'Periods',
                    'type': 'int',
                    'default': 0,
                    'input-type': 'text',
                    'optional': False,
                    'visibility_cond': [[
                        {
                            'param': '_1action',
                            'value': 'Create index column'
                        }
                    ], []],
                    'description': 'Number of periods  (keep 0 if using end date)'
                },
                '_8frequency': {
                    'label': 'Sampling frequency',
                    'type': 'str',
                    'default': 'D',
                    'input-type': 'text',
                    'optional': False,
                    'visibility_cond': [[], []],
                    'description': '(e.g : M) means monthly'
                },
                '_9fill_value': {
                    'label': 'Fill value',
                    'type': 'str',
                    'default': '0',
                    'input-type': 'text',
                    'optional': False,
                    'visibility_cond': [[], []],
                    'description': 'Fill value for reindexing (Completing missing dates).'
                }
            },
            "description": "This processor is used to index the entire dataframe. "
                           "You can choose to convert an existing column or create a new time index."
        }"""

        def _index(in_data):
            """Indexing local method"""
            action = _1action
            actions = ['Create index column',
                       'Convert index column to DateTime',
                       'Reindex the column']

            functions = [_create, _convert, _reindex]
            switcher = dict(zip(actions, functions))
            return switcher[action](in_data)

        def _range_index(in_data):
            """creating range index"""
            start = _5start_date
            end = _6end_date
            periods = None if not int(_7period) else int(
                _7period)  # TODO wait for John to make sense of type in the parameters
            end_ = end if not periods else None
            freq = _8frequency
            dt_params = {'Adapt index date': (start, None, in_data.shape[0], freq),
                         'Adapt Dataframe length': (start, end_, periods, freq),
                         'Adapt sampling frequency (Ignore frequency)': (start, end, in_data.shape[0], None)
                         }[_3element_to_adapt]

            prd_params = {'Adapt index date': (start, None, in_data.shape[0], freq),
                          'Adapt Dataframe length': (start, end_, periods, freq),
                          'Adapt sampling frequency (Ignore frequency)': (start, end_, periods, freq)
                          }[_3element_to_adapt]

            range_function = {'Date Time index': (pd.date_range, dt_params),
                              'Period Time index': (pd.period_range, prd_params)
                              }.get(_2index_type, (pd.date_range, dt_params))
            try:
                index = range_function[0](*range_function[1])
            except ValueError as e:
                raise ProcessorError(f'please verify parameters follow expected format :  {e}')
            return index

        def _create(in_data):
            """Function  for creating an index for the data frame"""
            index = _range_index(in_data)
            out_data = _apply_index(in_data, index)
            return out_data

        def _convert(in_data):
            """Converts the index of the input Data"""
            col = columns_to_process[0]  # TODO fix when drop-down fixed by John in front
            cols = in_data.columns
            if col not in cols:
                raise ProcessorError('column name not found in the input DataFrame')
            out_data = in_data
            out_data[col] = pd.to_datetime(out_data[col])
            out_data = out_data.set_index(col)
            return out_data

        def _reindex(in_data):
            """Reindex input Data"""
            col = columns_to_process[0]  # TODO fix to one value when front send one value
            cols = in_data.columns
            if col not in cols:
                raise ProcessorError('column name not found in the input DataFrame')
            out_data = in_data
            range_index = _range_index(out_data)
            out_data[col] = pd.to_datetime(out_data[col])
            out_data = out_data.set_index(col).reindex(range_index).fillna(_9fill_value)
            return out_data

        def _apply_index(in_data, index):
            """ Add index to the input data"""
            col = _4new_name
            cols = in_data.columns
            if col in cols:
                raise ProcessorError('column is already in the input DataFrame')

            df = pd.DataFrame({})
            df[col] = index
            out_data = pd.concat([df, in_data.reset_index()], axis=1)
            out_data = out_data[out_data[col].notnull()]
            out_data = out_data.set_index(col)
            return out_data.fillna(_9fill_value)

        self._df = _index(self._df)

    def _re_sample(self, columns_to_process, _1actions='Up sampling', _2new_freq='D', _3fill_method='None',
                   _4sample_method='None', _5fill_value=0.0, _6order=2, **kwargs):  # TODO make sense of type in params
        """{
            "name": "Resample as time series",
            "params": {
                'columns_to_process': {
                    'label': 'Index column',
                    'type': 'str',
                    'default': '',
                    'input-type': 'drop-down',
                    'optional': False,
                    'description': 'This column must be a DateTime index.'
                },
                '_1actions': {
                    'label': 'Action to perform',
                    'type': 'str',
                    'default': 'Up sampling',
                    'choices': ['Up sampling', 'Down sampling'],
                    'input-type': 'drop-down',
                    'optional' : False,
                    'description' :'Action to perform, either up sampling or down sampling.'
                },
                '_2new_freq': {
                    'label': 'New sampling frequency.',
                    'type': 'str',
                    'default': 'D',
                    'input-type': 'text',
                    'optional': False,
                    'description' : 'For instance (e.g : M) means monthly'
                },
                '_3fill_method': {
                    'label': 'Up sampling filling method',
                    'type': 'str',
                    'default': 'None',
                    'choices': ['None', 'Forward fill', 'Backward fill', 'Mean', 'Value', 'Linear interpolation',
                            'Spline interpolation'],
                    'input-type': 'drop-down',
                    'optional' : False,
                    'visibility_cond' : [[
                        {
                            'param' : '_1actions',
                            'value' : 'Up sampling'
                        }
                    ],[]],
                    'description' :'The filling method is the way to fill the gap due to upsampling'
                },
                '_4sample_method': {
                    'label': 'Down sampling method',
                    'type': 'str',
                    'default': 'None',
                    'choices': ['None', 'Mean', 'Median', 'First value', 'Last value', 'Sum'],
                    'input-type': 'drop-down',
                    'optional' :False,
                    'visibility_cond' : [[
                        {
                            'param' : '_1actions',
                            'value' : 'Down sampling'
                        }
                    ],[]],
                    'description' : 'The down sampling aggregation method is the way to aggregate data due to down '
                                    'sampling.'
                },
                '_5fill_value': {
                    'label': 'Filling Value',
                    'type': 'float',
                    'default': 0.0,
                    'input-type': 'text',
                    'optional' : False,
                    'visibility_cond' : [[
                        {
                            'param' : '_1actions',
                            'value' : 'Up sampling'
                        },
                        {
                            'param' : '_3fill_method',
                            'value' : 'Value'
                        },
                    ],[]],
                    'description' : 'Value with which to fill the gap. If "Value" is selected as up sampling filling method.'
                },
                '_6order': {
                    'label': 'Interpolation order',
                    'type': 'int',
                    'default': 2,
                    'input-type': 'text',
                    'optional' : False,
                    'visibility_cond' : [[
                        {
                            'param' : '_1actions',
                            'value' : 'Up sampling'
                        },
                        {
                            'param' : '_3fill_method',
                            'value' : 'Linear interpolation'
                        },
                    ],[
                        {
                            'param' : '_1actions',
                            'value' : 'Up sampling'
                        },
                        {
                            'param' : '_3fill_method',
                            'value' : 'Spline interpolation'
                        },
                    ]],
                    'description' : 'Interpolation order , if Interpolation strategy is selected as aggregation method.'
                    ' down sampling',
                }
            },
            "description": "Processor used for resampling Time series Data."
        }"""
        actions = ['Up sampling', 'Down sampling']
        up_sample_method = ['None', 'Forward fill', 'Backward fill', 'Mean', 'Value', 'Linear interpolation',
                            'Spline interpolation']
        down_sample_method = ['None', 'Mean', 'Median', 'First value', 'Last value', 'Sum']

        def _re_sample(in_data):
            """Up sample, Down sample, Shift, Lag the time series input Data"""
            new_freq = _2new_freq
            out_data = in_data
            sampled = out_data.resample(new_freq)

            functions = [_up_sample, _down_sample]
            out_data = dict(zip(actions, functions)).get(_1actions, 'Up sampling')(in_data, sampled)
            return out_data

        def _up_sample(in_data, sampled):
            out_data = in_data

            filled = [sampled.asfreq(),
                      sampled.ffill(),
                      sampled.bfill(),
                      sampled.asfreq().fillna(out_data.mean()),
                      sampled.asfreq().fillna(_5fill_value),
                      sampled.interpolate(method='linear', order=_6order),
                      sampled.interpolate(method='spline', order=_6order)]

            out_data = dict(zip(up_sample_method, filled)).get(_3fill_method, 'None')

            if len(out_data) < len(in_data):
                raise ProcessorError('please choose a higher frequency for up sampling.')
            return out_data

        def _down_sample(in_data, sampled):

            data_frames = [sampled.asfreq(_2new_freq),
                           sampled.mean(),
                           sampled.median(),
                           sampled.first(),
                           sampled.last(),
                           sampled.sum()]

            out_data = dict(zip(down_sample_method, data_frames)).get(_4sample_method, 'None')

            if len(out_data) > len(in_data):
                raise ProcessorError('please choose a lower frequency for down sampling.')
            return out_data

        self._df = _re_sample(self._df)

    def _normalize(self, columns_to_process, method='MinMaxScaler', feature_range_up=1, feature_range_down=0,
                   mode='Batch', scalar=100, s3_key='', **kwargs):
        """{
                'name': 'Normalize',
                "to_save" : True,
                'params': {
                    'columns_to_process': {
                        'label': 'Column(s) to process',
                        'type': 'str',
                        'default': [],
                        'input-type' : 'drop-down-list',
                        'optional': False,
                        'description': 'Column name to process.'
                    },
                    'method': {
                        'label': 'Normalize with',
                        'type': 'str',
                        'default': 'MinMaxScaler',
                        'choices': ['MinMaxScaler', 'Dividing First value'],
                        'input-type': 'drop-down',
                        'optional' : False,
                        'description' : 'Choose the normalizer to use.'
                    },
                    'feature_range_up': {
                        'label': 'Upper bound for feature range.',
                        'type': 'int',
                        'default': 1,
                        'input-type': 'text',
                        'optional': False,
                        'description': 'This is upper bound for the feature range to normalize the data.'
                    },
                    'feature_range_down': {
                        'label': 'Lower bound for feature range.',
                        'type': 'int',
                        'default': 0,
                        'input-type': 'text',
                        'optional': False,
                        'description': 'This is upper bound for the feature range to normalize the data.'
                    },
                    'scalar': {
                        'label': 'Scalar if using division by first value',
                        'type': 'int',
                        'default': 100,
                        'input-type': 'text',
                        'optional' : True,
                        'visibility_cond' :  [[
                            {
                                'param' : 'method',
                                'value' : 'Dividing First value'
                            }
                        ],[]],
                        'description':'Scalar to multiply the result of the division with the first value.'
                    },
                    'mode': {
                        'label': 'Normalization mode',
                        'type': 'str',
                        'default': 'Batch',
                        'choices': ['Batch', 'One by one'],
                        'input-type': 'drop-down',
                        'optional' : False,
                        'description' : 'If normalizing multiple columns.'
                    },
                },
                'description': 'This processor is used to normalize time series data inside DataFrame that is DateTime indexed.'
            }"""
        scalar = eval(str(scalar))  # TODO Wait for big John to make sense of types
        default_normalizer = {
            'MinMaxScaler': MinMaxScaler(feature_range=(0, 1)),
            'Dividing First value': ScalarNormalizer(scalar=scalar)
        }.get(method, MinMaxScaler(feature_range=(feature_range_down, feature_range_up)))
        if mode == 'One by one':
            for col in columns_to_process:
                try:
                    self._df[col] = self._apply_model_step(default_normalizer, self._df[col], s3_key=s3_key)
                except Exception as e:
                    raise ProcessorError(
                        f'cannot perform normalization with {col} check the type of this column, or try using\
                         batch normalization. {e}')
        else:
            try:
                self._df[columns_to_process] = self._apply_model_step(default_normalizer, self._df[columns_to_process],
                                                                      s3_key=s3_key)
            except Exception:
                raise ProcessorError(
                    f'cannot perform normalization with these columns, try using one by one normalization.')

    def _standardize(self, columns_to_process, mode='Batch', s3_key='', **kwargs):
        """{
            "name": "Standardize",
            "to_save" : True,
            "params" : {
                'columns_to_process': {
                    'label': 'Column(s) to process',
                    'type': 'str',
                    'default': [],
                    'input-type' : 'drop-down-list',
                    'optional': False,
                    'description': 'Column name to process.'
                },
                'mode': {
                        'label': 'Standardization mode',
                        'type': 'str',
                        'default': 'Batch',
                        'choices': ['Batch', 'One by one'],
                        'input-type': 'drop-down',
                        'optional' : False,
                        'description' : 'If standardizing multiple columns.'
                    },
            },
            "description": "Processor used for standardizing Data"
        }"""
        scaler = StandardScaler()
        if mode == 'Batch':
            try:
                self._df[columns_to_process] = self._apply_model_step(scaler, self._df[columns_to_process],
                                                                      s3_key=s3_key)
            except Exception as e:
                raise ProcessorError(
                    f'cannot perform standardization with these columns. Try it one by one to find out which \
                    column causes the error. {e}')
        else:
            for col in columns_to_process:
                try:
                    self._df[col] = self._apply_model_step(scaler, self._df[col], s3_key=s3_key)
                except Exception as e:
                    raise ProcessorError(
                        f'cannot perform standardization with {col}. Try batch standardization. {e}')

    def _smooth(self, columns_to_process, _1filters='Rolling window', _2method='Mean (Moving Average)',
                _3window_size='10', _4percentile='10 %', _5window_type='triang', _6sample_num=20, s3_key='', **kwargs):
        """{
            "name": "Smooth",
            "to_save" : True,
            'params': {
                'columns_to_process': {
                    'label': 'Column(s) to process',
                    'type': 'str',
                    'default': [],
                    'input-type' : 'drop-down-list',
                    'optional': False,
                    'description': 'Column name to process.'
                },
                '_1filters': {
                    'label': 'Filter to use',
                    'type': 'str',
                    'default': 'Rolling window',
                    'choices': ['Rolling window', 'Expanding window (Cumulative)', 'FIR filter'],
                    'input-type': 'drop-down',
                    'optional': False,
                    'description': 'The category filter to apply for smoothing the data',
                },
                '_2method': {
                    'label': 'Method to use',
                    'type': 'str',
                    'default': 'Mean (Moving Average)',
                    'choices': ['Mean (Moving Average)', 'Median', 'Percentile', 'Standard deviation',
                                'Sum (Default window type)', 'Product', 'Maximum', 'Minimum'],
                    'input-type': 'drop-down',
                    'optional': False,
                    'visibility_cond': [[  # AND
                        {
                            'param': '_1filters',
                            'value': 'Rolling window'

                        }], [  # OR
                        {
                            'param': '_1filters',
                            'value': 'Expanding window (Cumulative)'
                        }
                    ]
                    ],
                    'description': 'The method to apply for aggregating the data in the window',
                },
                '_3window_size': {
                    'label': 'Window size',
                    'type': 'str',
                    'default': '10',
                    'input-type': 'text',
                    'optional': False,
                    'visibility_cond': [[  # AND
                        {
                            'param': '_1filters',
                            'value': 'Rolling window'

                        }], [],  # OR
                    ],
                    'description': 'The window size to aggregate. This  may be integer or a period of DateTime.'
                },
                '_4percentile': {
                    'label': 'Percentile',
                    'type': 'str',
                    'default': '10 %',
                    'choices': ['10 %', '25 %', 'Median', '75 %', '90 %'],
                    'input-type': 'drop-down',
                    'optional': False,
                    'visibility_cond': [[  # AND
                        {
                            'param': '_1filters',
                            'value': 'Rolling window'

                        }], [  # OR
                        {
                            'param': '_1filters',
                            'value': 'Expanding window (Cumulative)'
                        }
                    ]
                    ],
                    'description': 'Percentile where to take the data.'
                },
                '_5window_type': {
                    'label': 'Window type (for FIR filter)',
                    'type': 'str',
                    'default': 'triang',
                    'choices': ['boxcar', 'triang', 'blackman', 'hamming', 'bartlett', 'parzen', 'bohman',
                                'blackmanharris',
                                'nuttall', 'barthann'],
                    'input-type': 'drop-down',
                    'optional': False,
                    'visibility_cond': [[
                        {
                            'param': '_1filters',
                            'value': 'FIR Filter'
                        }
                    ], []],
                    'description': 'Type of window to use to use.'
                },
                '_6sample_num': {
                    'label': 'Number of sample',
                    'type': 'int',
                    'default': 20,
                    'input-type': 'text',
                    'optional': False,
                    'visibility_cond': [[
                        {
                            'param': '_1filters',
                            'value': 'FIR Filter'
                        }
                    ], []],
                    'description': 'Number of sample to design the filter.'
                }
            },
            "description": "Processor used for smoothing time series data."
        }"""

        default_smoother = Smoother(columns_to_process, _1filters=_1filters, _2method=_2method,
                                    _3window_size=_3window_size, _4percentile=_4percentile,
                                    _5window_type=_5window_type, _6sample_num=_6sample_num)

        self._df = self._apply_model_step(default_smoother, self._df, s3_key=s3_key)

    def _return(self, columns_to_process, **kwargs):
        """{
            "name": "Calculate return (WIP)",
            'columns_to_process': {
                    'label': 'Column(s) to process',
                    'type': 'str',
                    'default': [],
                    'input-type' : 'drop-down-list',
                    'optional': False,
                    'description': 'Column name to process.'
                },
            "description": "Calculate return of a time series data."
        }"""
        pass

    # # --------------------------------------  HELPER FUNCTIONS  ----------------------------------------- #

    def _filter_value_remove_rows(self, index, value, df_value, match_mode):
        if match_mode == 'Substring':
            if value in df_value:
                self._df.drop(index, inplace=True)
        else:
            if value == df_value:
                self._df.drop(index, inplace=True)

    def _filter_value_keep_rows(self, index, value, df_value, match_mode):
        if match_mode == 'Substring':
            if value not in df_value:
                self._df.drop(index, inplace=True)
        else:
            if value != df_value:
                self._df.drop(index, inplace=True)

    @staticmethod
    def _apply_mode(value, df_value, norm_mode):
        norms = FILTER_NORM_MODES
        if isinstance(value, str):
            values = [(value, df_value), (value.lower(), df_value.lower()),
                      (ud.normalize('NFC', value),
                       ud.normalize('NFC', df_value))]
            val, df_val = dict(zip(norms, values)).get(norm_mode,
                                                       (value, df_value))
        else:
            val, df_val = value, df_value
        return val, df_val

    def _convert_value_to_col_type(self, col, value):
        try:
            type_ = self._df[col].dtype
            if not type_ == object:
                value = eval(value)
                value = {
                    type_ == np.int64: np.int64(value),
                    type_ == np.float64: np.float64(value),
                    type_ == np.int32: np.int32(value),
                    type_ == np.float32: np.float32(value),
                    type_ == np.int16: np.int16(value),
                    type_ == np.float16: np.float16(value)
                }.get(True, value)
        except Exception:
            raise ConversionError('please check your value parameter it may not match the column data type.')
        return value

    def _apply_model_step(self, estimator, *args, s3_key=''):
        """This uses the estimator to the arg and returns the result, saves to s3 or load from s3
        according to the mode :
            -> mode 'build' -> fit_transform,
            -> mode 'build_save' -> fit_transform then save to s3,
            -> mode 'use' -> load from s3 and transform
        """
        mode = self.mode
        arg = args[0]
        output = None
        if mode == 'build':
            try:
                output = estimator.fit_transform(arg)
            except Exception as e:
                raise ProcessorError(f'cannot fit the model {e}.')
            else:
                self.logger('Successfully fitted the model.')
        elif mode == 'build_save':
            try:
                output = estimator.fit_transform(arg)
            except Exception as e:
                raise ProcessorError(f'cannot fit the model {e}.')
            else:
                try:
                    self._save_model_to_s3(estimator, s3_key)
                except Exception as e:
                    raise ValueError(f'Could not save the model to S3 {e}.')
                else:
                    self.logger('Successfully saved the manipulation/processing step model to s3.')
        elif mode == 'use':
            try:
                estimator = self._load_model_from_s3(s3_key)
            except Exception as e:
                raise ProcessorError(f'cannot load the model form s3. {e}')
            else:
                output = estimator.transform(arg)
                self.logger('Successfully used manipulation/processing step model from S3.')
        return output

    def _save_model_to_s3(self, estimator, s3_key):

        _, file_path = mkstemp()
        joblib.dump(estimator, file_path)
        self._put_s3(s3_key, file_path)

    def _load_model_from_s3(self, s3_key):
        _, file_path = mkstemp()
        self._download_s3(file_path, s3_key)
        estimator = joblib.load(file_path)
        remove(file_path)
        return estimator

    def _download_s3(self, _file_path, _s3_key):
        with open(_file_path, 'wb') as f:
            self.s3_client.download_fileobj(self.s3_bucket_name, _s3_key, f)

    def _put_s3(self, _s3_key, _file_path):
        _url = self.s3_client.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': self.s3_bucket_name,
                'Key': _s3_key
            },
            ExpiresIn=120
        )
        with open(_file_path, 'rb') as data:
            put(_url, data=data)
        remove(_file_path)
