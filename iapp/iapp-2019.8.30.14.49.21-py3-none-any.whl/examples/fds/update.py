#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : update
# @Time         : 2019-08-30 13:58
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 
import os
"""

"""

def cmd(**kwargs):
    _ = os.popen(kwargs.get('cmd', 'ls')).read()
    return _
