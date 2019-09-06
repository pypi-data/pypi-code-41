# coding=utf-8

"""
定义基类
"""


import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseTester(ABC):
    """
    检验器基类.

    统计假设检验相关的类需要继承此类.
    """

    @abstractmethod
    def test(self):
        """
        实施假设检验.
        """
        raise NotImplementedError


class BaseDetector(ABC):
    """
    检测器基类.

    时间序列异常检测器需要继承此类.
    """

    @abstractmethod
    def detect(self):
        """
        检测时间序列中的异常.
        """
        raise NotImplementedError


class BaseForecaster(ABC):
    """
    预测器基类.

    时间序列预测器需要继承此类.
    """

    @abstractmethod
    def forecast(self):
        """
        预测.
        """
        raise NotImplementedError

    @abstractmethod
    def train(self):
        """
        训练.
        """
        raise NotImplementedError
