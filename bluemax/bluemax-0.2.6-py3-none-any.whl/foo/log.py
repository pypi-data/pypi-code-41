""" an example log setup """
import logging
import os
import yaml


def extend(config):  # pylint: disable=W0613
    """
    config is the existing logging configuration
    returning a dict will be used with dictConfig
    """
    if os.path.isfile("logging.yml"):
        logging.info("extending logging")
        with open("logging.yml", "r") as file:
            config = yaml.safe_load(file)
    return config
