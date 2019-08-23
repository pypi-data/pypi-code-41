#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Xiang Wang @ 2019-08-23 18:48:22


from __future__ import unicode_literals


class YunpianException(Exception):
    pass


class UserException(YunpianException):
    """客户那边的报错"""
    pass


class ClientException(YunpianException):
    """自己调用的错误"""
    pass


class NoHarassException(UserException):
    pass
