# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     help
   Description :
   Author :       jusk?
   date：          2019/8/31
-------------------------------------------------
   Change Activity:
                   2019/8/31:
-------------------------------------------------
"""

def sum(*values):
    s = 0
    for v in values:
        i = int(v)
        s = s + i
    print(s)

def output():
    print("http://xiaoh.me")