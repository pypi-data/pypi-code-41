#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2018 - 2019 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Script to determine the supported web browser variant.

It looks for QtWebEngine first and the old QtWebKit thereafter. It reports the
variant found or the string 'None' if both are absent.
"""

from __future__ import unicode_literals

import sys

variant = "None"

try:
    from PyQt5 import QtWebEngineWidgets    # __IGNORE_WARNING__
    variant = "QtWebEngine"
except ImportError:
    if sys.argv[-1].startswith("4."):
        try:
            from PyQt4 import QtWebKit      # __IGNORE_WARNING__
            variant = "QtWebKit"
        except ImportError:
            pass
    else:
        try:
            from PyQt5 import QtWebKit      # __IGNORE_WARNING__
            variant = "QtWebKit"
        except ImportError:
            pass

print(variant)      # __IGNORE_WARNING_M801__

sys.exit(0)
