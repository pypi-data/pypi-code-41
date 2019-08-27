#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-CLI.
# @File         : demo
# @Time         : 2019-07-16 20:38
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 


class A:

    def __init__(self, d={'x': 1, 'y': 2}):
        print(d)
        for k, v in d.items():
            setattr(self, k, v)
        print(self.x)


if __name__ == '__main__':
    A()