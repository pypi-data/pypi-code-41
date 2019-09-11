"""
Module providing helpers for panza's configuration
"""

from typing import Any, Dict

_config = {}


def init_config(values: Dict[str, Any]):
    """
    Initialize the configuration with given values

    :param values:              a dictionary used to initialize the configuration
    """
    global _config
    _config = values


def get_config() -> Dict[str, Any]:
    """
    Retrieve the configuration
    """
    return _config
