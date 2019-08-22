# -*- coding: utf-8 -*-

"""
DIALS Regression Data Manager
https://github.com/dials/data
"""

from __future__ import absolute_import, division, print_function

import pytest
import warnings

__all__ = ["pytest_addoption", "dials_data"]
__author__ = """Markus Gerstel"""
__email__ = "dials-support@lists.sourceforge.net"
__version__ = "2.0.22"
__commit__ = "fb1dd0282404d9cf6ca497c0645fcb70e4de2862"
__version_tuple__ = tuple(int(x) for x in __version__.split("."))


def pytest_addoption(parser):
    warnings.warn(
        "The dials_data import instructions have changed. Please check "
        "https://dials-data.readthedocs.io/en/latest/installation.html#as-a-developer-to-write-tests-with-dials-data"
        " for updated instructions",
        DeprecationWarning,
        stacklevel=2,
    )


@pytest.fixture
def dials_data():
    warnings.warn(
        "The dials_data import instructions have changed. Please check "
        "https://dials-data.readthedocs.io/en/latest/installation.html#as-a-developer-to-write-tests-with-dials-data"
        " for updated instructions",
        DeprecationWarning,
        stacklevel=2,
    )
    pytest.skip("dials_data import instructions need updating")
