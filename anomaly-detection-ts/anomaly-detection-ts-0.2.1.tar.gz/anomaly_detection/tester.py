# coding=utf-8

"""
Implementations of some statistical hypothesis tests.
"""

import logging

import numpy as np
from scipy import stats

from .base import BaseTester

logger = logging.getLogger(__name__)


class GrubbsTester(BaseTester):
    """
    Grubbs' Test for Outliers.

    Notes
    -----
    Grubbs' test is used to detect a single outlier in a univariate data set that follows an approximately normal distribution.

    It is defined for the hypothesis:

    - Null hypothesis: There are no outliers in the data set
    - Alternative hypothesis: There is exactly one outlier in the data set

    This is a full implementation of Grubbs' test as per https://www.itl.nist.gov/div898/handbook/eda/section3/eda35h1.htm

    Examples
    --------
    >>> x = np.array([199.31, 199.53, 200.19, 200.82, 201.92, 201.95, 202.18, 245.57])
    >>> g = GrubbsTester()
    >>> g.test(x)
    7
    """

    def test(self, data, alpha=0.05, mode='both'):
        """
        apply Grubbs' test.

        Parameters
        ----------
        data: array-like, 1d
            data set for detection.
        alpha : float, optional
            significance level (defaults to 0.05).
        mode : {'both', 'max', 'min'}, optional
            defaults to 'both', options are:

            - 'both': which means the two-sided version of the test will be applied.
            - 'max': to test whether the maximum value is an outlier.
            - 'min': to test whether the minimum value is an outlier.

        Returns
        -------
        None or int
            returns the index of the outlier if the null hypothesis is rejected. otherwise, returns None.
        """

        data = np.asarray(data)

        statistic, index = self.__statistic(data, mode)
        critical_value = self.__critical_value(data, alpha, mode)

        result = statistic > critical_value
        if result:
            return index
        return None

    @staticmethod
    def __critical_value(data, alpha, mode):
        N = len(data)
        if mode == 'both':
            t = stats.t.ppf(alpha / (2 * N), N - 2)
        else:
            t = stats.t.ppf(alpha / N, N - 2)
        return np.sqrt(t**2 / (N - 2 + t**2)) * (N - 1) / np.sqrt(N)

    @staticmethod
    def __statistic(data, mode):
        if mode == 'max':
            G = (np.max(data) - np.mean(data)) / np.std(data, ddof=1)
            index = np.argmax(data)
        elif mode == 'min':
            G = (np.mean(data) - np.min(data)) / np.std(data, ddof=1)
            index = np.argmin(data)
        elif mode == 'both':
            G = np.max(np.abs(data - np.mean(data))) / np.std(data, ddof=1)
            index = np.argmax(np.abs(data) - np.mean(data))
        else:
            raise ValueError("mode: expect 'max', 'min', or 'both',  get '{}'.".format(mode))

        return G, index


class TietjenMooreTester(BaseTester):
    """
    Tietjen-Moore Test for Outliers

    Notes
    -----
    The Tietjen-Moore test is used to detect multiple outliers in a univariate data set that follows an approximately normal distribution.

    It is defined for the hypothesis:

    - Null hypothesis: There are no outliers in the data set
    - Alternative hypothesis: There are exactly k outliers in the data set

    This is a full implementation of Tietjen-Moore test as per https://www.itl.nist.gov/div898/handbook/eda/section3/eda35h2.htm

    Examples
    --------
    >>> x = np.array([-1.40, -0.44, -0.30, -0.24, -0.22, -0.13, -0.05, 0.06, 0.10, 0.18, 0.20, 0.39, 0.48, 0.63, 1.01])
    >>> tm = TietjenMooreTester()
    >>> tm.test(x, 2)
    array([14,  0], dtype=int64)
    """

    def test(self, data, k, alpha=0.05, mode='both'):
        """
        apply Tietjen-Moore test.

        Parameters
        ----------
        data: array-like, 1d
            data set for detection.
        k : int
            amount of outliers in the alternative hypothesis.
        alpha : float, optional
            significance level (defaults to 0.05).
        mode : {'both', 'largest', 'smallest'}, optional
            defaults to 'both'. options are:

            - 'both': which means to test for outliers in both tails.
            - 'largest': to test whether the k largest points are outliers.
            - 'smallest': to test whether the k smallest points are outliers.

        Returns
        -------
        None or np.ndarray
            returns the indexes of the outliers if the null hypothesis is rejected. otherwise, returns None.
        """

        data = np.asarray(data)
        N = len(data)
        statistic, index = self.__statistic(data, k, mode)

        simulation = np.zeros(10000)
        for i in range(10000):
            norm = np.random.normal(size=N)
            simulation[i], _ = self.__statistic(norm, k, mode)
        critical_value = np.quantile(simulation, alpha)

        result = statistic < critical_value

        if result:
            return index
        return None

    @staticmethod
    def __statistic(data, k, mode):
        if mode == 'both':
            r = np.abs(data - np.mean(data))
            indices = np.argsort(r)
        elif mode == 'largest':
            indices = np.argsort(data)
        elif mode == 'smallest':
            indices = np.argsort(0 - data)
        else:
            raise ValueError("mode: expect 'both', 'largest', or 'smallest', get '{}'".format(mode))
        y = data[indices]
        index = indices[-k:]
        statistic = np.sum((y[:-k] - np.mean(y[:-k]))**2) / np.sum((y - np.mean(y))**2)
        return statistic, index


class GESDTester(BaseTester):
    """
    Generalized ESD Test for Outliers

    Notes
    -----
    The generalized ESD (extreme Studentized deviate) test is used to detect one or more outliers in a univariate data set that follows an approximately normal distribution.

    It is defined for the hypothesis:

    - Null hypothesis: There are no outliers in the data set
    - Alternative hypothesis: There are up to r outliers in the data set

    This is a full implementation of generalized ESD test as per https://www.itl.nist.gov/div898/handbook/eda/section3/eda35h3.htm

    Examples
    --------
    >>> x = np.array([-0.25, 0.68, 0.94, 1.15, 1.20, 1.26, 1.26, 1.34, 1.38, 1.43, 1.49, 1.49, 1.55, 1.56, 1.58, 1.65, 1.69, 1.70, 1.76, 1.77, 1.81, 1.91, 1.94, 1.96, 1.99, 2.06, 2.09, 2.10, 2.14, 2.15, 2.23, 2.24, 2.26, 2.35, 2.37, 2.40, 2.47, 2.54, 2.62, 2.64, 2.90, 2.92, 2.92, 2.93, 3.21, 3.26, 3.30, 3.59, 3.68, 4.30, 4.64, 5.34, 5.42, 6.01])
    >>> x
    array([-0.25,  0.68,  0.94,  1.15,  1.2 ,  1.26,  1.26,  1.34,  1.38,
            1.43,  1.49,  1.49,  1.55,  1.56,  1.58,  1.65,  1.69,  1.7 ,
            1.76,  1.77,  1.81,  1.91,  1.94,  1.96,  1.99,  2.06,  2.09,
            2.1 ,  2.14,  2.15,  2.23,  2.24,  2.26,  2.35,  2.37,  2.4 ,
            2.47,  2.54,  2.62,  2.64,  2.9 ,  2.92,  2.92,  2.93,  3.21,
            3.26,  3.3 ,  3.59,  3.68,  4.3 ,  4.64,  5.34,  5.42,  6.01])
    >>> gesd = GESDTester()
    >>> gesd.test(x, 10, report=True)
    H0: there are no outliers in the data
    H1: there are up to 10 outliers in the data
    <BLANKLINE>
    Significance level: α = 0.05
    Critical region: Reject H0 if Ri > critical value
    <BLANKLINE>
    Summary Table for Two-Tailed Test
    -----------------------------------------
          Exact           Test       Critical
      Number of      Statistic     Value, λi
    Outliers, i      Value, Ri            5 %
    -----------------------------------------
              1          3.119          3.159
              2          2.943          3.151
              3          3.179          3.144 *
              4          2.810          3.136
              5          2.816          3.128
              6          2.848          3.120
              7          2.279          3.112
              8          2.310          3.103
              9          2.102          3.094
             10          2.067          3.085
    -----------------------------------------
    array([53, 52, 51])
    """

    def test(self, data, r, alpha=0.05, report=False):
        """
        apply the generalized ESD test

        Parameters
        ----------
        data: array-like, 1d
            data set for detection.
        r : int
            the upper bound of the amount of outliers in the alternative hypothesis.
        alpha : float, optional
            significance level (defaults to 0.05).
        report : bool, optional
            whether to print the report of the test (defaults to False).

        Returns
        -------
        None or np.ndarray
            returns the indexes of the outliers if the null hypothesis is rejected. otherwise, returns None.
        """

        data = np.asarray(data)

        R, index = self.__statistic(data, r)
        L = self.__critical_value(data, r, alpha)
        count = -1
        for i in range(r):
            if R[i] > L[i]:
                count = i
        if report:
            self.__report(r, alpha, R, L)
        return index[:count + 1]

    @staticmethod
    def __statistic(data, r):
        data = np.copy(data)
        indices = np.arange(data.size)
        R = np.zeros(r)
        index = np.zeros(r, dtype=int)
        for i in range(r):
            R[i] = np.max(np.abs(data - np.mean(data))) / np.std(data, ddof=1)
            idx = np.argmax(np.abs(data - np.mean(data)))
            index[i] = indices[idx]
            data = np.delete(data, idx)
            indices = np.delete(indices, idx)
        return R, index

    @staticmethod
    def __critical_value(data, r, alpha):
        N = len(data)
        L = np.zeros(r)
        for i in range(r):
            t = stats.t.ppf(1 - alpha / (2 * (N - i)), N - i - 2)
            L[i] = (N - i - 1) * t / np.sqrt((N - i - 2 + t**2) * (N - i))
        return L

    @staticmethod
    def __report(r, alpha, R, L):
        rep = [
            'H0: there are no outliers in the data',
            'H1: there are up to {:d} outliers in the data'.format(r),
            '',
            'Significance level: α = {:.2f}'.format(alpha),
            'Critical region: Reject H0 if Ri > critical value',
            '',
            'Summary Table for Two-Tailed Test',
            '-----------------------------------------',
            '      Exact           Test       Critical',
            '  Number of      Statistic     Value, λi',
            'Outliers, i      Value, Ri{:13.0f} %'.format(100 * alpha),
            '-----------------------------------------'
        ]
        for i in range(r):
            line = '{:11d}{:15.3f}{:15.3f}'.format(i + 1, R[i], L[i])
            if R[i] > L[i]:
                line += ' *'
            rep.append(line)
        rep.append('-----------------------------------------')
        print('\n'.join(rep))


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
