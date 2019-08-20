# !/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created on MAY 21, 2018
@author: zhanglanhui
homepage recommender:ffm
"""
import hashlib
import time


def hashstr(s, nr_bins):
    return str(int(hashlib.md5(s.encode('utf-8')).hexdigest(), 16) % (nr_bins - 1) + 1)


def print_run_time(func):
    def wrapper(*args, **kw):
        local_time = time.time()
        func(*args, **kw)
        print('Current function : {function}, time used : {temps}'.format(
            function=func.__name__, temps=time.time() - local_time))

    return wrapper
