#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : model_update
# @Time         : 2019-08-29 16:58
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  :
import os

os.environ['--checkpoint'] = '/Users/yuanjie/Desktop/Projects/Python/tql-App/model_update/DATA'

from iapp import App
from utils.magic import magic_app, magic_model_maps, checkpoint

app = App()
app.app = magic_app


def predict(**kwargs):
    model_name = kwargs["model_name"]  # sklearn_lr_demo.model
    (predict, feature_transform) = magic_model_maps.get(model_name)
    X = feature_transform(**kwargs)  # 二维数组
    return predict(X)


app.add_route('/deploy', predict, methods="POST", num_model=len(magic_model_maps), checkpoint=checkpoint)
app.run()
