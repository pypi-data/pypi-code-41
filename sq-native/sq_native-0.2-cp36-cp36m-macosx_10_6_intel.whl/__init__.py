# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
"""Sqreen Python Native Module"""
import ctypes
import logging
import os
import sys

import pkg_resources

LOGGER = logging.getLogger(__name__)


def load_library(name):
    """Load a native library located in this module."""

    ext = "dylib" if os.name == "posix" and sys.platform == "darwin" else "so"
    fn = pkg_resources.resource_filename("sq_native", name + "." + ext)
    if fn is None:
        root_dir = os.path.dirname(os.path.abspath(__file__))
        fn = os.path.join(root_dir, name + "." + ext)

    try:
        LOGGER.debug("Loading %s", fn)
        return ctypes.cdll.LoadLibrary(fn)
    except OSError:
        LOGGER.warning("%s was not loaded", name)


lib = load_library("libSqreen")

__all__ = ["load_library", "lib"]
