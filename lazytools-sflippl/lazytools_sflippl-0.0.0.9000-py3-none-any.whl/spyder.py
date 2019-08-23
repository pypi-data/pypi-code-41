#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 13:23:20 2019

@author: sflippl
"""

import os

def in_spyder():
    """
    Check whether code is executed in Spyder.
    Credit goes to: https://stackoverflow.com/a/17755798/11813441
    """
    return any('SPYDER' in name for name in os.environ)