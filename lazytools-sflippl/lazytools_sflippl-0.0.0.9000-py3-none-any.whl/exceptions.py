#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 12:35:52 2019

@author: sflippl
"""

import sys
from lazytools.spyder import in_spyder

def raise_from(e, msg, new_e = TypeError):
    """
    Safeguard for missing raise from functionality in Spyder, see 
    https://github.com/spyder-ide/spyder/issues/2943.
    Simply issues raise msg from e outside of Spyder.
    
    Credit goes to: https://stackoverflow.com/a/6062799/11813441
    """
    if in_spyder():
        raise new_e(msg + '(' + str(e) + ')').with_traceback(sys.exc_info()[2])
    else:
        raise new_e(msg) from e