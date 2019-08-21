"""
Miscelania of utilities.
"""
import os


def eval_env_as_boolean(varname, standard_value=None):
    if standard_value is None:
        return str(os.getenv(varname)).lower() in ("true", "1", "t", "y")

    return str(os.getenv(varname, standard_value)).lower() in ("true", "1", "t", "y")
