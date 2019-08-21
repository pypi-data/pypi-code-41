# -*- coding: utf-8 -*-
"""
module flow_main.py
--------------------
Main flow application module.
"""
import os
import sys
import tensorflow as tf
from .config import Config
import numpy as np
import pickle
import time
from blinker import signal


class FlowMain(object):
    """ Project main class.
    """
    __config_path__ = "../settings/flow.cfg"

    def __init__(self, session: tf.Session=None):
        """Main module initialization."""
        self.config = self.get_config()

        # TODO: session configuration from file
        if session is None:
            self.tf_sess = tf.Session()
        else:
            self.tf_sess = session
        # setting current session to keras
        tf.keras.backend.set_session(self.tf_sess)

    @classmethod
    def get_config(cls):
        """ A configuration loader function.
        Builds the configuration object, loads the configuration from the specified files
        and then returns it.
        :return: a Config object.
        """
        config = Config()
        config.add_path(cls.__config_path__)
        # load tripod configuration
        config.load_config()
        return config