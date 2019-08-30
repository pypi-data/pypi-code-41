#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : sklearn.lgb.ctr
# @Time         : 2019-08-29 18:05
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  :


def feature_transform(**kwargs):
    """

    :param kwargs:
    :return: 返回二维数组 model.predict(X)
    """

    return [[kwargs.get('x', 1)]]
