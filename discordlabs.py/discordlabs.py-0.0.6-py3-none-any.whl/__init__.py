__title__ = 'discordlabs.py'
__author__ = 'Anish Anne'
__license__ = 'MIT'
__copyright__ = 'Copyright 2019 Anish Anne'
__version__ = '0.0.6'

name="discordlabs"
from .client import Client
from collections import namedtuple

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')

version_info = VersionInfo(major=0, minor=0, micro=6, releaselevel='final', serial=0)