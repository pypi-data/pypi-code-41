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
import argparse
import numpy as np
import pickle
import time
from blinker import signal


class FlowMain(object):
    """ Project main class.
    """

    def __init__(self, session: tf.Session=None, config_name=None, config_path=None):
        """Main module initialization."""
        self._arg_parser = argparse.ArgumentParser()
        self._arg_parser.add_argument("-s", "--settings", help="The settings file name.", default="flow.cfg")
        self._arg_parser.add_argument(
            "-b", "--settings_base_path",
            help="The settings base path.", default="../settings/",
        )
        self._args = self._arg_parser.parse_args()
        if config_name is not None:
            self._args.settings = config_name
        if config_path is not None:
            self._args.settings_base_path = config_path

        self.config = self.get_config()

        # TODO: session configuration from file
        if session is None:
            self.tf_sess = tf.Session()
        else:
            self.tf_sess = session
        # setting current session to keras
        tf.keras.backend.set_session(self.tf_sess)

    def get_config(self):
        """ A configuration loader function.
        Builds the configuration object, loads the configuration from the specified files
        and then returns it.
        :return: a Config object.
        """
        # build config file path from args
        base_path = self._args.settings_base_path
        file = self._args.settings
        path = os.path.join(base_path, file)
        # creates config file and adds the built config path to it
        config = Config()
        config.add_path(path)
        # load tripod configuration
        config.load_config()
        return config
