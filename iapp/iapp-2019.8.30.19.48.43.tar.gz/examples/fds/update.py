#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : downloda
# @Time         : 2019-08-30 13:32
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

import os
import yaml
import requests
from pathlib import Path
from itertools import chain
from .ModelPredictor import ModelPredictor

# models 加入环境变量
models = os.environ['--models']
os.sys.path.append(models)

# models home
fds = "http://cnbj1.fds.api.xiaomi.com/browser-algo-nanjing/models/"

# 下载配置文件
config_url = fds + "config.yml"
_ = requests.get(config_url, timeout=10).text
config = yaml.safe_load(_)
print(config)

# 新建models文件夹： /home/work
create_path = lambda path: Path(path).mkdir(parents=True, exist_ok=True)
create_path(models)

# 下载并加载
for file in chain(*config.items()):
    os.popen(f'wget {fds + file} -O {models}/{file}').read()

model2transformer = {}
for model_file, transformer_file in config.items():
    model_type = model_file.split('_')[0]
    print(f"{models}/{model_file}")
    predict = ModelPredictor().predictor(f"{models}/{model_file}", model_type)
    feature_transform = __import__(transformer_file[:-3]).feature_transform
    model2transformer[model_file] = predict, feature_transform

# Tricks:
# auto_reload 监控update.py 热更新：设置环境变量不奏效
# 可通过环境变量设置 全局变量
