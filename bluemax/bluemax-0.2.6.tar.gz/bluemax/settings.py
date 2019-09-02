""" We load our settings here """
from collections.abc import Mapping
import os
import importlib
import logging
import yaml

LOGGER = logging.getLogger(__name__)

SETTINGS = {}


def extend(extension, value):
    """ extension is a qname, resolved and run with value """
    mdl, func = extension.split(":")
    func = getattr(importlib.import_module(mdl), func)
    return func(value)


def merge_dict(dct, merge_dct):
    for key, val in merge_dct.items():
        if isinstance(dct.get(key), dict) and isinstance(val, Mapping):
            dct[key] = merge_dict(dct[key], val)
        else:
            dct[key] = val
    return dct


def init_settings(filename=None):
    """ load a config yaml file """
    filename = filename if filename else os.getenv("config", "settings.yml")
    if os.path.isfile(filename):
        LOGGER.info("loading settings from %s", filename)
        with open(filename, "r") as file:
            SETTINGS.update(yaml.safe_load(file))
    else:
        SETTINGS["settings"] = "local"  # stop rentrance


def get_settings(name, default=None):
    """
        access to settings - load is automatic
        if the settings cannot be found the getenv
        will be returned
    """
    if not SETTINGS:
        init_settings()
    return SETTINGS.get(name, os.getenv(name, default))
