#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : xx
# @Time         : 2019-08-29 21:03
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 


import requests

files = {'model': open('sklearn_lr_demo.model', 'rb'),
         'feature_transformer': open('sklearn_lr_demo.py', 'rb')}
print(requests.get("http://0.0.0.0:8000/upload", files=files).text)


print(__import__('sklearn_lr_demo').feature_transform)
