# coding=utf-8

"""
Implementation of data emulator.
"""

import numpy as np
from scipy.signal import lfilter


class Emulator:
    """
    数据仿真器.

    用于生成时间序列和时间序列中的异常值.

    使用 ARMA 过程生成时间序列.

    支持 4 种类型的异常, 分别是 innovational outlier (IO)，additive outlier (AO)，level shift (LS) 以及 temporary change (TC).

    Parameters
    ----------
    ar : list
        ARMA 模型中的自回归项.
    ma : list
        ARMA 模型中的移动平均项.
    size : int, optional
        时间序列的长度, 默认为 500
    scale : float, optional
        ARMA 模型中误差的量级, 默认为 1.0
    pattern : list, optional
        周期性序列的生成模式, 默认为 None, 即生成的序列为非周期性序列

    Notes
    -----
    关于 ARMA 模型, 请参考 https://en.wikipedia.org/wiki/Autoregressive%E2%80%93moving-average_model.

    关于时间序列中的异常, 请参考 https://www.jianshu.com/p/4b11ddd0de97.

    Examples
    --------
    >>> import numpy as np
    >>> ar = [1., 0.8]
    >>> ma = [1., 0.7]
    >>> emlt = Emulator(ar, ma)
    >>> seq = emlt.sequence() # 生成时间序列
    >>> tau = [100, 278, 300] # 异常的位置
    >>> omega = 10 # 异常的量级
    >>> anml = emlt.anomalies(tau, omega) # 生成异常
    >>> seq_anml = seq + anml
    >>> x = np.linspace(0, np.pi, 100, endpoint=False)
    >>> pattern = 8*np.sin(x) + 2*np.cos(2*x) + 2*np.sin(4*x) # 周期图样
    >>> seq_seasonal = emlt.sequence(pattern=pattern) # 生成周期性时间序列
    """

    def __init__(self, ar, ma, **kwargs):
        size = kwargs.get('size', 500)
        scale = kwargs.get('scale', 1.)
        pattern = kwargs.get('pattern')

        self.__ar = ar
        self.__ma = ma
        self.__size = size
        self.__scale = scale
        self.__pattern = pattern

    @property
    def ar(self):
        """
        ARMA 模型中的自回归项.
        """

        return self.__ar

    @property
    def ma(self):
        """
        ARMA 模型中的移动平均项.
        """

        return self.__ma

    @property
    def size(self):
        """
        时间序列的长度.
        """

        return self.__size

    @property
    def scale(self):
        """
        ARMA 模型中误差的量级.
        """

        return self.__scale

    @property
    def pattern(self):
        """
        周期性序列的生成模式.
        """

        return self.__pattern

    @pattern.setter
    def pattern(self, pattern):
        self.__pattern = pattern

    def sequence(self, **kwargs):
        """
        生成时间序列.

        Parameters
        ----------
        size : int, optional
            时间序列的长度, 默认为 self.size
        scale : float, optional
            ARMA 模型中误差的量级, 默认为 self.scale
        pattern : list, optional
            周期性序列的生成模式, 默认为 self.pattern

        Returns
        -------
        np.ndarray
            生成的时间序列.
        """
        size = kwargs.get('size', self.size)
        scale = kwargs.get('scale', self.scale)
        pattern = kwargs.get('pattern', self.pattern)

        seq = self.__arma_process(
            ar=self.ar,
            ma=self.ma,
            size=size,
            scale=scale
        )
        if pattern is not None:
            seq = self.__seasonal(pattern=pattern, sequence=seq)
        return seq

    def anomalies(self, tau, omega, category='ao', **kwargs):
        """
        生成时间序列中的异常

        Parameters
        ----------
        tau : int or array-like
            异常的位置.
        omega : float or array-like
            异常的量级.
        category : {'ao', 'io', 'tc', 'ls'}, optional
            异常的类型, 默认为 'ao'.
        size : int, optional
            时间序列的长度, 默认为 self.__size
        delta : float, optional
            异常类型为 'tc' 时使用的衰减系数, 默认为 0.9

        Returns
        -------
        numpy.ndarray
            生成的异常数据.
        """

        size = kwargs.get('size', self.__size)

        if isinstance(tau, (list, tuple, np.ndarray)):
            if min(tau) < 0 or max(tau) >= size:
                raise ValueError("indexes of anomalies out of range.")
            if isinstance(omega, (list, tuple, np.ndarray)):
                if len(tau) != len(omega):
                    raise ValueError("length of tau does not match length of omega.")
            elif isinstance(omega, (int, float)):
                pass
            else:
                raise TypeError("omega is expected to be numerical or array-like, '{}' is got.".format(type(omega).__name__))
        elif isinstance(tau, int):
            if tau < 0 or tau >= size:
                raise ValueError("index of anomaly out of range.")
            if not isinstance(omega, (int, float)):
                raise TypeError("omega is expected to be numerical with tau being 'int', however '{}' is got.".format(type(omega).__name__))
        else:
            raise TypeError(
                "tau is expected to be 'int' or array-like, '{}' is got.".format(type(tau).__name__))

        e = np.zeros(size)
        e[tau] = omega

        if category == 'io':
            return self.__arma_process(self.__ar, self.__ma, size, e=e)
        if category == 'ao':
            return e
        if category == 'tc':
            delta = kwargs.get('delta', 0.9)
            if delta <= 0 or delta >= 1:
                raise ValueError("delta out of range.")
            return self.__arma_process([1, -delta], [1], size, e=e)
        if category == 'ls':
            return self.__arma_process([1, -1], [1], size, e=e)
        raise ValueError("category: expect 'io', 'ao', 'tc', or 'ls', get '{}'".format(category))

    @staticmethod
    def __arma_process(ar, ma, size, scale=1., e=None):
        if e is None:
            e = np.random.normal(size=size)
        return lfilter(ma, ar, scale * e)

    @staticmethod
    def __seasonal(pattern, sequence):
        n = len(pattern)
        m = len(sequence)
        assert m >= n * 2, "length of sequence must be greater than twice of length of pattern."
        ret = np.zeros_like(sequence)
        for i in range(m):
            ret[i] = sequence[i] + pattern[i % n]
        return ret
