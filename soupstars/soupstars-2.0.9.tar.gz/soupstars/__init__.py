import pkg_resources

from .core import parse, SoupStar
from .client import Client

__version__ = pkg_resources.require("soupstars")[0].version
