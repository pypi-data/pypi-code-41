# coding=utf-8

"""
Implementations of some time series forecasters.
"""

import logging

import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from .base import BaseForecaster

logger = logging.getLogger(__name__)


class HoltWintersForecaster(BaseForecaster):
    """
    Holt-Winters Forecaster.

    Notes
    -----
    Holt-Winters' 模型又称为三次指数平滑模型, 可以用来预测带有周期性的时间序列. 除了三次指数平滑之外, HoltWintersForecaster 也支持一次和二次指数平滑.

    关于指数平滑方法, 请参考 https://www.jianshu.com/p/2c607fe926f0.
    """

    def forecast(self, data, **kwargs):
        """
        预测时间序列的下一个值.

        Parameters
        ----------
        data : array-like, 1d
            时间序列.
        fitted_params : dict
            训练好的模型参数, 形如 {'smoothing_level': 0.8, 'smoothing_slope': 0.1, 'smoothing_seasonal': 0.7}.
        trend : {"add", "mul", "additive", "multiplicative", None}, optional
            趋势分量的类型.
        seasonal : {"add", "mul", "additive", "multiplicative", None}, optional
            季节分量的类型.
        seasonal_periods : int, optional
            季节的长度, 亦即时间序列的周期, 当 seasonal 不为 None 时必需提供此参数.

        Raises
        ------
        TypeError
            fitted_params 缺失.

        Returns
        -------
        float
            预测值.
        """

        data = np.asarray(data)

        fitted_params = kwargs.get('fitted_params')
        if not fitted_params:
            raise TypeError('fitted_params is required.')

        trend = kwargs.get('trend')
        seasonal = kwargs.get('seasonal')
        seasonal_periods = kwargs.get('seasonal_periods')

        model = ExponentialSmoothing(
            data,
            trend=trend,
            seasonal=seasonal,
            seasonal_periods=seasonal_periods
        )
        result = model.fit(optimized=False, **fitted_params)
        forecast = result.forecast()[0]
        return forecast

    def train(self, data, **kwargs):
        """
        训练模型.

        Parameters
        ----------
        data : array-like, 1d
            时间序列.
        trend : {"add", "mul", "additive", "multiplicative", None}, optional
            趋势分量的类型.
        seasonal : {"add", "mul", "additive", "multiplicative", None}, optional
            季节分量的类型.
        seasonal_periods : int, optional
            季节的长度, 亦即时间序列的周期, 当 seasonal 不为 None 时必需提供此参数.

        Returns
        -------
        dict
            训练好的模型参数, 形如 {'smoothing_level': 0.8, 'smoothing_slope': 0.1, 'smoothing_seasonal': 0.7}.
        """

        data = np.asarray(data)

        trend = kwargs.get('trend')
        seasonal = kwargs.get('seasonal')
        seasonal_periods = kwargs.get('seasonal_periods')

        model = ExponentialSmoothing(
            data,
            trend=trend,
            seasonal=seasonal,
            seasonal_periods=seasonal_periods
        )
        result = model.fit()
        fitted_params = {
            'smoothing_level': result.params['smoothing_level'],
            'smoothing_slope': result.params['smoothing_slope'],
            'smoothing_seasonal': result.params['smoothing_seasonal']
        }
        return fitted_params


class ARIMAForecaster(BaseForecaster):
    """
    ARIMA Forecaster (TODO)

    Notes
    -----
    关于 ARIMA 模型, 请参考 https://www.jianshu.com/p/e52a4b82654e.

    """

    # TODO: ARIMA Forecaster
    def forecast(self, data, **kwargs):
        pass

    def train(self, data, **kwargs):
        pass
