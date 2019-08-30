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

# models home
home = Path("http://cnbj1.fds.api.xiaomi.com/browser-algo-nanjing/models")

# 下载配置文件
config_url = home / "config.yml"
_ = requests.get(config_url, timeout=10).text
config = yaml.safe_load(_)
print(config)

for k, v in config.items():
    os.popen("mkdir ./models/")






