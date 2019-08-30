#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : app_run
# @Time         : 2019-08-30 13:51
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 
"""
通过在main文件
"""

from iapp import App

import yaml
import requests

# models home
home = "http://cnbj1.fds.api.xiaomi.com/browser-algo-nanjing/models/"

# 下载配置文件
config_url = home + "config.yml"
_ = requests.get(config_url, timeout=10).text
config = yaml.safe_load(_)
print(config)


from examples.fds import cmd


app = App()
app.add_route('/cmd', cmd)
app.run()


