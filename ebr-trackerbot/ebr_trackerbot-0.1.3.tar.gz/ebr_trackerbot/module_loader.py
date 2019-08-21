"""
Loader module
"""

import os
import importlib
import logging


def load(path, package_name):
    """
    Loads all python modules from specified path
    """
    globals_variables = globals()

    if not os.path.exists(path):
        return

    for file in os.listdir(path):
        if file == "__init__.py":
            continue
        if not os.path.isfile(path + "/" + file):
            continue
        mod_name = file[:-3]  # strip .py at the end
        try:
            globals_variables[mod_name] = importlib.import_module("." + mod_name, package=package_name)
        except ImportError as err:
            logging.error("Can not load module '%s' in folder '%s'. Error: %s", mod_name, path, str(err))
