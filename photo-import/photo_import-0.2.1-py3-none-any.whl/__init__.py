"""
Photo-Import
~~~~~~
A tool for importing photos from one directory into a hierarchical folder
structure in another directory based on the EXIF data of the photos.

:copyright: Copyright 2019 Edward Armitage.
:license: MIT, see LICENSE for details.
"""
from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions
