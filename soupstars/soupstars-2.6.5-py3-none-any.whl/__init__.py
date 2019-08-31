import pkg_resources

from .core import parse, SoupStar  # noqa
from .client import Client  # noqa


__version__ = pkg_resources.require("soupstars")[0].version
