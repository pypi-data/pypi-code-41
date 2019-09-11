#!/usr/bin/env python3
# coding: utf-8

# Built-in packages

# External packages
import numpy as np

# Internal packages

# TODO : convert to cython


class TimeSeries:
    """ TimeSeries is a 1 dimensional array of floating numbers.

    Attributes
    ----------
    series : np.ndarray[ndim=1, dtype=np.float64]
        The series of values.
    time_index : np.ndarray[ndim, dtype=int or str or datetime]
        Time index of series.
    T : int
        Size of the `series`.

    Methods
    -------

    """
    def __init__(self, series, index=None, kind_returns='raw', signal=None):
        """ """
        self.series = np.asarray(series).flatten()
        self.T = self.series.size
        if index is None:
            self.index = range(len(series))
        else:
            self.index = index

    # TODO : __get__, __set__ methods


# =========================================================================== #
#                              Financial Series                               #
# =========================================================================== #


class FySeries(TimeSeries):
    """ FySeries is a 1 dimensional array of floating number. It's can be a
    series of prices of an asset or index values or performances.

    Attributes
    ----------
    series : np.ndarray[ndim=1, dtype=np.float64]
        The series of values.
    time_index : np.ndarray[ndim=1, dtype=int or str or datetime]
        Time index of the series.
    returns : np.ndarray[ndim=1, dtype=np.float64]
        Returns of the series.
    T : int
        Size of the `series`.
    kind_returns : str
        Design the method to compute returns: 'raw' is the first difference,
        'log' is logarithmic returns and 'perc' is returns in percentage.

    Methods
    -------

    """
    def __init__(self, series, index=None, kind_returns='raw'):
        """ """
        # TODO : verify dimension of series
        self.series = np.asarray(series, dtype=np.float64).flatten()
        self.T = self.series.size
        if index is None:
            self.index = np.arange(len(series), dtype=int)
        else:
            self.index = index
        self.kind_returns = kind_returns
        self.returns = _comp_returns(series, kind_returns=kind_returns)

    def __get__(self, i_0, i_T, i=1):
        return self.series[i_0: i_T: i]

    def get_ret(self, i_0):
        pass


class StratSeries(FySeries):
    """ StratSeries is a 1 dimensional array of floating number. performances
    or index values of a financial strategy.

    Attributes
    ----------
    series : np.ndarray[ndim=1, dtype=np.float64]
        The series of values.
    time_index : np.ndarray[ndim=1, dtype=int or str or datetime]
        Time index of the series.
    returns : np.ndarray[ndim=1, dtype=np.float64]
        Returns of the series.
    signal : np.ndarray[ndim=1, dtype=np.float64]
        Signal of strategy.
    T : int
        Size of the `series`.
    kind_returns : str
        Design the method to compute returns: 'raw' is the first difference,
        'log' is logarithmic returns and 'perc' is returns in percentage.

    Methods
    -------

    """
    def __init__(self, series, index=None, kind_returns='raw', signal=None):
        """ """
        self.series = np.asarray(series).flatten()
        self.T = self.series.size
        if index is None:
            self.index = range(len(series))
        else:
            self.index = index
        self.kind_returns = kind_returns
        self.returns = _comp_returns(series, kind_returns=kind_returns)
        if signal is None:
            self.signal = np.ones([])


def _comp_returns(series, kind_returns='raw'):
    # Set 1d array
    returns = np.zeros([len(series)])
    # Check kind of returns asked
    if kind_returns == 'raw':
        returns[1:] = series[1:] - series[:-1]
    elif kind_returns == 'log':
        returns[1:] = np.log(series[1:] / series[:-1])
    elif kind_returns == 'perc':
        returns[1:] = series[1:] / series[:-1] - 1
    else:
        raise ValueError(str(kind_returns) + ' not allowed.')

    return returns


def comp_returns(series, kind_returns='raw'):
    """ Compute returns for one period of series of prices or performances or
    index values.

    Parameters
    ----------
    series: np.ndarray[ndim=1, dtype=np.float64]
        Time-series of prices, performances or index values.
    kind_returns : str, optional
        Kind of returns TODO : available parameters.

    Returns
    -------
    out : np.ndarray[ndim=1, dtype=np.float64]
        Time-series of returns for one period.

    Examples
    --------
    TODO

    See Also
    --------
    TODO

    """
    if (series[:-1] <= 0).any() and kind_returns != 'raw':
        description_error = 'Series containing null or negative numbers not '
        description_error += 'allowed with log and percentage kind of returns.'
        raise ValueError(description_error)
    return _comp_returns(series, kind_returns=kind_returns)


# =========================================================================== #
#                              Financial array                                #
# =========================================================================== #

# TODO : __setitem__, __iter__, __add__, and other operators methods

class farray:
    """ This object is a financial array.

    Attributes
    ----------
    series : np.ndarray[ndim=1, dtype=np.float64]
        A time-series of prices, performances or index values.
    returns : np.array[ndim=1, dtype=np.float64]
        A time-series of returns on one period of `series`.

    Methods
    -------
    __getitem__ : Return a slice of `series` or `returns`.
    __repr__ : Display series and returns.

    """
    def __init__(self, series):
        """ Set a financial array.

        Parameters
        ----------
        series : np.ndarray[ndim=1, dtype=np.float64]
            A time-series of prices, performances or index values.

        """
        self.series = np.asarray(series, dtype=np.float64)
        self.returns = np.zeros(series.shape)
        self.returns[1:] = series[1:] - series[:-1]

    def __getitem__(self, keys):
        """ Return a slice of `series` or `returns`.

        Parameters
        ----------
        keys : int, slice, or tuple of int, slice or str
            If int or slice return the corresponding part of `series`. If
            tuple first parameters must be slice or int, and last one must
            be a string.

        Returns
        -------
        out : np.ndarray[ndim=1, dtype=np.float64]
            `series` or `returns`

        Examples
        --------
        >>> a = farray([100, 80, 120, 150, 120, 130])
        >>> a[:]
        array([100., 80., 120., 150., 120., 130.])
        >>> a[:, 'ret']
        array([0., -20., 40., 30., -30., 10.])
        >>> a
        Series:
        array([100., 80., 120., 150., 120., 130.])
        Returns:
        array([0., -20., 40., 30., -30., 10.])

        """
        if isinstance(keys, slice) or isinstance(keys, int):
            return self.series[keys]
        elif isinstance(keys, tuple):
            if keys[-1] == 'ret':
                return self.returns[keys[:-1]]
            else:
                raise ValueError(str(kind) + ' not allowed')
        else:
            raise IndexError(str(type(keys)) + ' type not allowed')

    def __repr__(self):
        """ Display series and returns.

        Returns
        -------
        out : str
            Values of `series` and `returns`.

        """
        txt = 'Series:\n'
        txt += str(self.series)
        txt += '\nReturns:\n'
        txt += str(self.returns)
        return txt
