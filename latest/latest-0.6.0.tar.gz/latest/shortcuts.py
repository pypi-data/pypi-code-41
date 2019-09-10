""":mod:`shortcuts` module contains shortcut functions built upon core functionality of :mod:`latest` package.

"""
from .config import config as Config
from .core import Grammar


def render(template, data, config=Config):
    """Render a template within a context.

    Args:
        template (str): the template.
        data (dict): the context.
        config (config._Config): configuration object.

    Returns:
        str: the output of the evaluation process as defined by :mod:`latest` core functions.
    """

    return Grammar(config).eval(template, data)
