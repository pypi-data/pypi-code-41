#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialization for Plot Twist Tools
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

print('='*100)
print('| Plot Twist Pipeline | > Loading Plot Twist Tools')

try:
    import plottwist as pt
    from maya import cmds
    cmds.evalDeferred('pt.init()')
    print('| Plot Twist Pipeline | Plot Twist Tools loaded successfully!')
    print('='*100)
except Exception as e:
    try:
        import plottwist as pt
        pt.init()
        print('| Plot Twist Pipeline | Plot Twist Tools loaded successfully!')
        print('='*100)
    except Exception as e:
        print('ERROR: Impossible to load Plot Twist Tools, contact TD!')
        print(str(e))
