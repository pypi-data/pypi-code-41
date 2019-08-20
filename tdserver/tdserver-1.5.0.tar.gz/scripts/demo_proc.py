#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 Tongdun Inc. All Rights Reserved.
# @Time             : 2019/8/17 10:49 AM
# @Author           : ding
# @File             : demo_api.py
# @description      :

from tdserver import ImageServer


if __name__ == '__main__':
    d = ImageServer('http://0.0.0.0:8080/inference')
    req = d.send({"a": 1, "b": "hello world!"})
    print(req)
