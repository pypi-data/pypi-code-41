from os import path

from qmenta.core import version
from .Account import Account
from .Project import Project
from .Subject import Subject

try:
    __version__ = version.read(path.dirname(__file__))
except IOError:
    # VERSION file was not created yet
    __version__ = '0.dev0'

__all__ = [
    'Account',
    'Project',
    'Subject'
]
