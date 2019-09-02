#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : Predictor
# @Time         : 2019-08-29 19:04
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

import joblib


class ModelPredictor(object):

    def __init__(self):
        pass

    def predictor(self, filename, model_type='sklearn'):
        """

        :param kwargs:
        :return:
        """
        return self.__getattribute__(f"model_{model_type}")(filename)

    def model_sklearn(self, filename):
        return joblib.load(filename).predict_proba

    def model_keras(self, filename):
        pass

    def model_tensorflow(self, filename):
        pass


if __name__ == '__main__':
    filename = "/Users/yuanjie/Desktop/Projects/Python/tql-App/model_update/DATA/sklearn_lr_demo.model"

    ModelPredictor().predictor(filename)