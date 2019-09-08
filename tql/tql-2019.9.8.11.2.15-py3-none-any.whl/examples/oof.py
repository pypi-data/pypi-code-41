#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-Python.
# @File         : oof
# @Time         : 2019-09-07 23:44
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

from tql.algo_ml.oof import OOF, LGB
from sklearn.datasets import make_classification
from sklearn.metrics import roc_auc_score
X, y = make_classification(1000)
clf = LGB()
clf.fit(X, y, X, feval=roc_auc_score)