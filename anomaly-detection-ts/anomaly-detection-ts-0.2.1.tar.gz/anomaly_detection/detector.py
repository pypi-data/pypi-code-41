# coding=utf-8

"""
Implementations of some detectors.
"""

import logging

import numpy as np
import pandas as pd
from pywt import wavedec, waverec
from scipy.fftpack import fft, ifft
from statsmodels.tsa.seasonal import seasonal_decompose

from .base import BaseDetector
from .tester import GESDTester, GrubbsTester, TietjenMooreTester

logger = logging.getLogger(__name__)


class DirectDetector(BaseDetector):
    """
    直接检测器.

    DirectDetector 用来检测平稳序列中的异常值.

    提供 4 种基于阈值的检测方法和 3 种基于统计假设检验的检测方法, 分别是:

    - threshold: 固定阈值法, 超出上界/下界的值被判定为异常值.
    - k_sigma: k-sigma 法, 偏离均值超过 k 倍 sigma 的值被判定为异常值.
    - k_iqr: k-iqr 法, 偏离上/下四分位数超过 k 倍四分位间隔 (interquartile range, iqr) 的值被判定为异常值.
    - cusum: 累积和检测法, 用来检测序列是否发生均值漂移.
    - grubbs: Grubbs' 假设检验, 详见 tester.GrubbsTester.
    - tm: Tietjen-Moore 假设检验, 详见 tester.TietjenMooreTester.
    - gesd: generalized ESD (extreme Studentized deviate) 假设检验, 详见 tester.GESDTester.
    """

    def __init__(self):
        super().__init__()
        self.__method_map = {
            'threshold': self.__threshold_detect,
            'k_sigma': self.__k_sigma_detect,
            'k_iqr': self.__k_iqr_detect,
            'cusum': self.__cusum_detect,
            'grubbs': self.__grubbs_detect,
            'tm': self.__tietjen_moore_detect,
            'gesd': self.__gesd_detect,
        }
        self.__testers = {
            'grubbs': GrubbsTester(),
            'tm': TietjenMooreTester(),
            'gesd': GESDTester(),
        }

    def detect(self, data, **kwargs):
        """
        检测异常.

        Parameters
        ----------
        data : array-like, 1d
            待检测的数据.
        method : {'threshold', 'k_sigma', 'k_iqr', 'cusum', 'grubbs', 'tm', 'gesd'}, optional
            决定使用哪种方法来检测序列中的异常值, 默认为 'k_sigma'. 每种检测法都有各自的参数, 如下所示.

        Other Parameters
        ----------------
        ub : float, optional
            threshold 检测法的参数, 时有效, 上界
        lb : float, optional
            threshold 检测法的参数, 时有效, 下界
        k : float, optional
            k_sigma 检测法的参数, 默认为 3.0
        mu : float, optional
            k_sigma 检测法的参数, 默认为 data 的均值
        sigma : float, optional
            k_sigma 检测法的参数, 默认为 data 的标准差
        k : float, optional
            k_iqr 检测法的参数, 默认为 1.5
        k : float, optional
            cusum 检测法的参数, 默认为 1.0
        h : float, optional
            cusum 检测法的参数, 默认为 6.0
        alpha : float, optional
            grubbs 检测法的参数, 假设检验的显著性水平, 默认为 0.05.
        mode : {'both', 'max', 'min'}, optional
            grubbs 检测法的参数, 默认为 'both', 详见 tester.GrubbsTester.
        k : int, optional
            tm 检测法的参数, 异常值的数量, 默认为 1， 详见 tester.TietjenMooreTester.
        alpha : float, optional
            tm 检测法的参数, 假设检验的显著性水平, 默认为 0.05.
        mode : {'both', 'largest', 'smallest'}, optional
            tm 检测法的参数, 默认为 'both', 详见 tester.TietjenMooreTester.
        r : int, optional
            gesd 检测法的参数, 异常值的最大数量, 默认为 len(data)//6, 详见 tester.GESDTester.
        alpha : float, optional
            gesd 检测法的参数, 假设检验的显著性水平, 默认为 0.05.
        length : int, optional
            检测的数据长度，检测器会检测 data[-length:] 中的异常，默认等于 len(data).

        Raises
        ------
        TypeError
            使用固定阈值检测法时既没有提供上界也没有提供下界.

        Returns
        -------
        numpy.ndarray
            用来指示异常值的布尔索引.
        """
        logger.debug(kwargs)

        data = pd.Series(data).fillna(method='bfill').values
        length = kwargs.get('history_length', len(data))
        data = data[-length:]

        method = kwargs.get('method', 'k_sigma')
        if method not in self.__method_map:
            raise ValueError('unknown method: %s' % method)
        return self.__method_map[method](data, **kwargs)

    @staticmethod
    def __threshold_detect(data, **kwargs):
        ret = np.full(data.shape, False)

        ub = kwargs.get('ub')
        lb = kwargs.get('lb')

        if ub:
            ret |= (data > ub)
        if lb:
            ret |= (data < lb)

        if not any([ub, lb]):
            raise TypeError('Neither upper bound nor lower bound is provided.')
        return ret

    @staticmethod
    def __k_sigma_detect(data, **kwargs):
        k = kwargs.get('k', 3.)

        mu = kwargs.get('mu', np.mean(data))
        sigma = kwargs.get('sigma', np.std(data, ddof=1))

        ub = mu + k * sigma  # upper bound
        lb = mu - k * sigma  # lower bound
        return (data > ub) | (data < lb)

    @staticmethod
    def __k_iqr_detect(data, **kwargs):
        k = kwargs.get('k', 1.5)

        q1 = np.quantile(data, 0.25)
        q3 = np.quantile(data, 0.75)
        iqr = q3 - q1
        upper = q3 + k * iqr
        lower = q1 - k * iqr
        return (data > upper) | (data < lower)

    @staticmethod
    def __cusum_detect(data, **kwargs):
        k = kwargs.get('k', 1.0)
        h = kwargs.get('h', 6.0)

        mean = np.mean(data)
        std = np.std(data, ddof=1)
        size = len(data)

        p = 0
        m = 0
        ret = np.empty(size, dtype=bool)

        for i, x in enumerate(data):
            new_p = max(0, p + x - mean - k * std)
            new_m = min(0, m + x - mean + k * std)

            if (new_p > p and new_p > h * std) or (new_m < m and new_m < -h * std):
                ret[i] = True
            else:
                ret[i] = False

            p = new_p
            m = new_m

        return ret

    def __grubbs_detect(self, data, **kwargs):
        alpha = kwargs.get('alpha', 0.05)
        mode = kwargs.get('mode', 'both')

        result = np.full(data.shape, False)
        index = self.__testers['grubbs'].test(data, alpha=alpha, mode=mode)
        if index is not None:
            result[index] = True
        return result

    def __tietjen_moore_detect(self, data, **kwargs):
        k = kwargs.get('k', 1)
        alpha = kwargs.get('alpha', 0.05)
        mode = kwargs.get('mode', 'both')

        result = np.full(data.shape, False)
        index = self.__testers['tm'].test(data, k=k, alpha=alpha, mode=mode)
        if index is not None:
            result[index] = True
        return result

    def __gesd_detect(self, data, **kwargs):
        r = kwargs.get('r', len(data) // 6)
        alpha = kwargs.get('alpha', 0.05)

        result = np.full(data.shape, False)
        index = self.__testers['gesd'].test(data, r=r, alpha=alpha)
        if index is not None:
            result[index] = True
        return result


class FFTDetector(BaseDetector):
    """
    快速傅里叶变换检测器.

    FFTDetector 用来检测周期性数据中的异常值.

    先用快速傅里叶变换将原数据从时域转换到频域, 滤掉低频信号, 再将高频信号转换回时域, 最后使用 DirectDetector 检测高频信号中的异常值.

    Notes
    -----
    关于傅里叶变换, 请参考 https://www.jianshu.com/p/1cd1231e6422.
    """

    def __init__(self):
        super().__init__()
        self.__core_detector = DirectDetector()

    def detect(self, data, **kwargs):
        """
        检测异常.

        Parameters
        ----------
        data : array-like, 1d
            待检测的数据.
        critical : float, optional
            过滤低频信号的阈值, 频率低于 critical * Nyquist 频率的信号会被过滤, 默认为 0.3.
        method : {'threshold', 'k_sigma', 'k_iqr', 'cusum', 'grubbs', 'tm', 'gesd'}, optional
            决定使用哪种方法来检测高频信号中的异常值, 默认为 'k_sigma'.

            此外, 每种检测方法都有其相应的参数, 详见 DirectDetector.

        Returns
        -------
        numpy.ndarray
            用来指示异常值的布尔索引.
        """

        data = pd.Series(data).fillna(method='bfill').values

        resid = self.__get_resid(data, **kwargs)
        result = self.__core_detector.detect(resid, **kwargs)
        return result

    def __get_resid(self, data, **kwargs):
        critical = kwargs.get('critical', 0.3)
        F = fft(data)
        filt = self.__get_filter(len(F), critical)
        return ifft(np.multiply(F, filt))

    @staticmethod
    def __get_filter(sample, critical):
        if critical <= 0 or critical >= 1:
            raise ValueError("critical out of range.")
        filt = np.zeros(sample)
        idx = int(sample * critical / 2)
        filt[idx: sample - idx] = 1
        return filt


class DWTDetector(BaseDetector):
    """
    离散小波变换检测器.

    DWTDetector 用来检测周期性数据中的异常值.

    先用离散小波变换将原数据从时域转换到频域, 滤掉低频分量, 再将高频分量转换回时域, 最后使用 DirectDetector 检测高频信号中的异常值.

    Notes
    -----
    关于小波变换, 请参考 https://www.jianshu.com/p/9bad9466ad21.
    """

    def __init__(self):
        super().__init__()
        self.__core_detector = DirectDetector()

    def detect(self, data, **kwargs):
        """
        检测异常.

        Parameters
        ----------
        data : array-like, 1d
            待检测的数据.
        wavelet : str, optional
            小波函数, 默认为 'db4', 详见 https://pywavelets.readthedocs.io/en/latest/ref/wavelets.html.
        detail : int, optional
            保留的高频分量, 默认为 2.
        method : {'threshold', 'k_sigma', 'k_iqr', 'cusum', 'grubbs', 'tm', 'gesd'}, optional
            决定使用哪种方法来检测高频信号中的异常值, 默认为 'k_sigma'.

            此外, 每种检测方法都有其相应的参数, 详见 DirectDetector.

        Returns
        -------
        numpy.ndarray
            用来指示异常值的布尔索引.
        """
        data = pd.Series(data).fillna(method='bfill').values

        resid = self.__get_resid(data, **kwargs)
        result = self.__core_detector.detect(resid, **kwargs)
        return result

    @staticmethod
    def __get_resid(data, **kwargs):
        wavelet = kwargs.get('wavelet', 'db4')
        detail = kwargs.get('detail', 2)
        coeffs = wavedec(data, wavelet=wavelet)
        for i in range(len(coeffs) - detail):
            coeffs[i] *= 0
        return waverec(coeffs, wavelet)


class STLDetector(BaseDetector):
    """
    STL 检测器.

    STLDetector 用来检测周期性数据中的异常值.

    使用 STL (Seasonal and Trend decomposition using Loess) 方法将时间序列分解为季节、趋势和残差, 然后用 DirectDetector 检测残差中的异常值.
    """

    def __init__(self):
        super().__init__()
        self.__core_detector = DirectDetector()

    def detect(self, data, **kwargs):
        """
        检测异常.

        Parameters
        ----------
        data : array-like, 1d
            待检测的数据.
        seasonal_periods : int
            时间序列的周期.
        method : {'threshold', 'k_sigma', 'k_iqr', 'cusum', 'grubbs', 'tm', 'gesd'}, optional
            决定使用哪种方法来检测高频信号中的异常值, 默认为 'k_sigma'.

            此外, 每种检测方法都有其相应的参数, 详见 DirectDetector.

        Returns
        -------
        numpy.ndarray
            用来指示异常值的布尔索引.
        """
        data = pd.Series(data).fillna(method='bfill').values

        resid = self.__get_resid(data, **kwargs)
        result = self.__core_detector.detect(resid, **kwargs)
        return result

    @staticmethod
    def __get_resid(data, **kwargs):
        freq = kwargs.get('seasonal_periods')
        if freq is None:
            raise ValueError('specified seasonal_periods is required.')
        stl = seasonal_decompose(
            data,
            model='additive',
            freq=freq,
            extrapolate_trend='freq'
        )
        return stl.resid + stl.trend


class CWTDetector(BaseDetector):
    # TODO: CWT Detector
    def __init__(self):
        super(CWTDetector, self).__init__()
        self.__core_detector = DirectDetector()

    def detect(self, data, **kwargs):
        pass
