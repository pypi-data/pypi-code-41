# -*- coding: utf-8 -*-

# Copyright (c) 2017 - 2019 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing some utilities for Google Safe Browsing.
"""

from __future__ import unicode_literals

import sys

if sys.version_info < (3, 0):
    def toHex(value):
        """
        Public method to convert a bytes array to a hex string.
        
        @param value value to be converted
        @type bytes
        @return hex string
        @rtype str
        """
        return value.encode("hex")
else:
    def toHex(value):
        """
        Public method to convert a bytes array to a hex string.
        
        @param value value to be converted
        @type bytes
        @return hex string
        @rtype str
        """
        return value.hex()
