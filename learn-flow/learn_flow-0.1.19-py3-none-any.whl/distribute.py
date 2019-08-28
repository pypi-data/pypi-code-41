# -*- coding: utf-8 -*-
"""
module distribute.py
--------------------
Training procedure distribution strategy.
Encapsulates the tensor flow distributed strategy methods.
"""
import tensorflow as tf
import numpy as np
from blinker import signal
from .config.config import Config
from .learner import DefaultLearner
from .dataset import Dataset
import time


class Strategy(object):
    """ Wrapper for distribution strategies.
    """
    def __init__(self, strategy_type="mirrored"):
        """
        Strategy wrapper initialization.
        :param strategy_type: the strategy name. Allowed values: 'mirrored'
        """
        self.config = Config()
        self.strategy_type = strategy_type
        self.visible_devices = self.get_available_gpus()
        if self.strategy_type.lower() == "mirrored":
            self.distributed_strategy = tf.distribute.MirroredStrategy(devices=self.visible_devices)
        else:
            raise ValueError("Strategy type not recognized.")
        self.distributed_strategy.scope().__enter__()
        self.distributed_strategy.unwrap

    def get_available_gpus(self):
        """
        Get the name of all available gpus.
        :return: a list of all available gpus.
        """
        from tensorflow.python.client import device_lib
        all_devices = device_lib.list_local_devices()
        gpus = [x.name for x in all_devices if x.device_type == "GPU"]
        return gpus

