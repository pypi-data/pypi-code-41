#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : main
# @Time         : 2019-08-30 17:31
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 


import os

os.environ['--models'] = '/Users/yuanjie/Desktop/Projects/Python/tql-App/examples/fds/models'
os.environ['--flag'] = '/Users/yuanjie/Desktop/Projects/Python/tql-App/examples/fds'
flag = __import__('hotflag').flag

from iapp import App
from examples.fds.update import model2transformer

app = App()


def predict(**kwargs):
    model_name = kwargs["model_name"]  # sklearn_lr_demo.model
    (predict, feature_transform) = model2transformer.get(model_name)
    X = feature_transform(**kwargs)  # 二维数组
    return predict(X)


app.add_route('/deploy', predict, methods="POST", flag=flag)
app.run()
