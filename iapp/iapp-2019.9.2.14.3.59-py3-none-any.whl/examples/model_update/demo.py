#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : demo
# @Time         : 2019-08-29 18:17
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 
import os
from pathlib import Path
os.sys.path.append("/Users/yuanjie/Desktop/Projects/Python/tql-App/model_update/DATA/")
#
# p = Path(__file__)
# print(p.absolute())
#
#
print(__import__('sklearn_lr_demo'))

import importlib

print(importlib.import_module('sklearn_lr_demo').feature_transform)

# import yaml
# import fire
#
# def f(**kwargs):
#     return yaml.dump(kwargs, open('config.yml', 'w'))
#
#
# if __name__ == '__main__':
#     fire.Fire(f)