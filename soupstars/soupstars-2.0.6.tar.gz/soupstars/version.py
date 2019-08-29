import os

from .helpers import package_dirname


version_abspath = os.path.join(package_dirname, 'version.txt')

with open(version_abspath, 'r') as f:
    __version__ = f.read().strip()
