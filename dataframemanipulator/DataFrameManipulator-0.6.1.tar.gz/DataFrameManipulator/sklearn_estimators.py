import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator
from sklearn.impute import SimpleImputer


class ScalarNormalizer(BaseEstimator):
    def __init__(self, scalar=100):
        """For normalizer classifier"""
        self._scalar = scalar
        self._firsts = None

    def fit(self, X):
        """Training method for the normalizer"""
        assert (type(self._scalar) == int)
        if isinstance(X, pd.DataFrame):
            self._firsts = {col: X[col][0] for col in X.columns}
        else:
            self._firsts = [i[0] for i in X]

        return self

    @property
    def first_values(self):
        """First values of the dataframe or the array"""
        return self.first_values

    def transform(self, X):
        """transforms the data"""
        try:
            getattr(self, "_firsts")
        except AttributeError:
            raise RuntimeError("You must train the ScalarNormalize first !")
        if isinstance(X, pd.DataFrame):
            for col in X.columns:
                try:
                    divisor = self._firsts[col]
                    X[col] = X[col].apply(lambda x: (x / divisor) * self._scalar)
                except KeyError as e:
                    raise KeyError(f'ERROR, check your parameters {e} is not found.')
                except ValueError as e:
                    raise ValueError(f'ERROR, value error check your parameters.')
        return X

    def fit_transform(self, X):
        """Train the normalizer the transform the data."""

        assert (type(self._scalar) == int)
        if isinstance(X, pd.DataFrame):
            self._firsts = {col: X[col][0] for col in X.columns}
        else:
            self._firsts = [i[0] for i in X]
        if isinstance(X, pd.DataFrame):
            for col in X.columns:
                divisor = self._firsts[col]
                X[col] = X[col].apply(lambda x: (x / divisor) * self._scalar)
        return X


class MissingValuesHandler(BaseEstimator):
    """ Handling means imputing, or dropping missing values from array of arrays or pandas DataFrame"""
    NOT_IMPLEMENTED_MSG = 'Cannot use this handler with array of arrays data-type.' \
                          'This functionality is not implemented yet.'

    def __init__(self, columns='any', missing_values=np.nan, axis=0, strategy='drop', fill_value=None, verbose=0):
        """Initialize all attributes used along the methods."""

        self.check_right_type(missing_values, columns, strategy, axis)

        self._verbose = verbose
        self._strategy = strategy
        self._columns = columns
        self._axis = axis
        self._missing_values = missing_values
        self._fill_value = fill_value
        self._imps = None

    def fit(self, x):
        """Fit with an array of arrays or a pandas.DataFrame data-type
        :param x : DataFrame
        :return self
        """
        self._assert_input_type(x)
        if self._strategy != 'drop':
            self._check_column_existence(x)
            self._imps = self._get_imp()
            for col in self._columns:
                try:
                    self._imps[col].fit(x[col].values.reshape(-1, 1))
                except ValueError:
                    raise ValueError(
                        f'Cannot use "{self._strategy}" strategy to fit handler with "{col}",'
                        f' check column type, or check if there are some Infinity (NaN) values.')
        else:
            print('No need to fit the data for dropping Strategy...')
        return self

    def transform(self, x):
        """Return a transformed Data.
        :param x : DataFrame to be transformed
        :return y : transformed DataFrame
        """

        y = x.copy()
        if self._strategy == 'drop':
            y = self._drop(x)
        else:
            self._check_column_existence(x)
            for col in self._columns:
                y[col] = self._imps[col].transform(x[col].values.reshape(-1, 1))
        return y

    def fit_transform(self, x):
        """Calls fit then transform.
        :param x : DataFrame to be transformed
        :return y : transformed DataFrame
        """

        self.fit(x)
        y = self.transform(x)
        return y

    @property
    def columns(self):
        """All used columns."""
        return self._columns

    def _drop(self, x):
        """When using the drop strategy."""

        if isinstance(self._columns, list):
            y = x.dropna(subset=self._columns, axis=self._axis)
        else:
            y = x.dropna(how=self._columns, axis=self._axis)
        return y

    @staticmethod
    def check_right_type(missing_value, columns, strategy, axis):
        """For checking  passed arguments respect types."""

        # ===== Columns ===== #
        try:
            assert isinstance(columns, list) or isinstance(columns,
                                                           str) or columns is None, 'Columns must be of type list of str any/all'
        except AssertionError as e:
            raise TypeError(f'{e} , got {columns.__class__.__name__} .')

        # ===== Missing values ===== #
        try:
            assert isinstance(missing_value, np.nan.__class__) or isinstance(missing_value, str) or isinstance(
                missing_value, int), 'Missing values placeholder must be np.nan or of type int of str any/all'
        except AssertionError as e:
            raise TypeError(f'{e} , got "{missing_value}"" of type {missing_value.__class__.__name__} .')

        # ===== Strategy ===== #
        try:
            assert isinstance(strategy, str), 'Strategy must be of type str.'
        except AssertionError as e:
            raise TypeError(f'{e} , got {strategy.__class__.__name__} .')

        # ===== axis ===== #
        try:
            assert axis in [0, 1, 'index', 'columns'], 'axis must be either :  { 0, 1, "index", "columns" }'
        except AssertionError as e:
            raise TypeError(f'{e} , got "{axis}" .')

    def _check_column_existence(self, x):
        """Checking column existence"""
        try:
            assert isinstance(self._columns,
                              list), 'If not using "drop" strategy,' \
                                     ' columns must be of type list with at list one element.'
        except AssertionError as e:
            raise TypeError(f'{e} , got {self._columns.__class__.__name__} .')

        for col in self._columns:
            try:
                assert col in x.columns, f'"{col}" not found in the DataFrame.'
            except AssertionError as e:
                raise KeyError(str(e))

    def _get_imp(self):
        """Returns a dict of untrained SimpleImp"""

        return {col: SimpleImputer(missing_values=self._missing_values,
                                   strategy=self._strategy,
                                   fill_value=self._fill_value,
                                   verbose=self._verbose) for col in self._columns}

    @staticmethod
    def _assert_input_type(x):
        try:
            assert isinstance(x, pd.DataFrame)  # x is a DataFrame
        except AssertionError:  # x is an array of arrays
            raise NotImplemented(MissingValuesHandler.NOT_IMPLEMENTED_MSG)


class Smoother(BaseEstimator):
    """Fit with no padding, and transform pad it, it operates on dataframe, arrays, series, etc...."""

    def __init__(self, columns_to_process, _1filters='Rolling window', _2method='Mean (Moving Average)',
                 _3window_size='10', _4percentile='10 %', _5window_type='triang', _6sample_num=20, **kwargs):

        self.columns_to_process = columns_to_process
        self.filter_ = _1filters
        self.method = _2method
        self.window_size = _3window_size
        self.percentile = _4percentile
        self.window_type = _5window_type
        self.num_sample = _6sample_num

    def fit(self, data):
        """ Apply the smoothing"""
        # There is nothing to do here
        return self

    def transform(self, data):
        """ Add padding and apply the smoothing"""
        if self.filter_ != 'Expanding window (Cumulative)':
            pad_length = self.window_size if self.filter_ == "Rolling window" else self.num_sample
            pad_length -= 1
            pad_dict = {}
            for col in data.columns:
                pad_dict[col] = [data[col].mean()] * pad_length \
                    if col in self.columns_to_process else ['<missing>'] * pad_length
            pad_df = pd.DataFrame(pad_dict)
            frames = [pad_df, data]
            padded_data = pd.concat(frames)

            out_data = self._apply_smoothing(padded_data)
            missing_value = MissingValuesHandler(missing_values='<missing>')
            return missing_value.fit_transform(out_data)
        else:
            return self._apply_smoothing(data)

    def fit_transform(self, data):
        """ Apply the smoothing """
        return self._apply_smoothing(data)

    def _apply_smoothing(self, data):
        """Smoothing method for smoother modules."""
        filter_ = self.filter_
        method = self.method
        window_size = self.window_size
        percentile = self.percentile
        window_type = self.window_type
        num_sample = self.num_sample
        cols = self.columns_to_process
        out_data = data
        if window_size.isdigit():
            window_size = int(window_size)
        for col in cols:
            try:
                windowed = {
                    'Rolling window': data[col].rolling(window=window_size),
                    'Expanding window (Cumulative)': data[col].expanding()
                }[filter_]
            except KeyError:
                try:
                    out_data[col] = data[col].rolling(window=int(num_sample), win_type=window_type).sum()
                except Exception:
                    raise ValueError('cannot smooth the column, please check your parameters.')
            else:
                if method == 'Percentile':
                    p_tile = {
                        '10 %': 0.1,
                        '25 %': 0.25,
                        'Median': 0.5,
                        '75 %': 0.75,
                        '90 %': 0.9,
                    }.get(percentile, 0.5)
                    out_data[col] = windowed.quantile(p_tile)
                elif method == 'Product':
                    if filter_ == 'Rolling window':
                        raise ValueError('Cumulative product is not applicable for rolling window.')
                    out_data[col] = data[col].cumprod()
                else:
                    out_data[col] = {
                        'Mean (Moving Average)': windowed.mean(),
                        'Median': windowed.quantile(0.5),
                        'Standard deviation': windowed.agg(['std']),
                        'Sum (Default window type)': windowed.sum(),
                        'Maximum': windowed.max(),
                        'Minimum': windowed.min()
                    }.get(method, windowed.mean())
        return out_data
