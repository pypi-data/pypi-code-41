#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : scheduler
# @Time         : 2019-09-02 13:17
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

import asyncio
from datetime import datetime, time, timedelta
from sanic_scheduler import SanicScheduler, task

import jieba
from iapp import App

pred1 = lambda **kwargs: kwargs['x'] + kwargs['y']
pred2 = lambda x=1, y=1: x - y
pred3 = lambda text='小米是家不错的公司': jieba.lcut(text)

app = App(debug=True)
app.add_route("/f1", pred1, version="1")
app.add_route("/f2", pred2, version="2")
app.add_route("/f3", pred3, version="3", methods="POST")

scheduler = SanicScheduler(app.app, False)  # CST 非 UTC

count = {}

# TODO：集成到tql-APP
@task(timedelta(seconds=3), time(hour=13, minute=57))  # 13:57:00后 3秒一次调度
def hello(app):
    print(count)
    count['n'] = count.get('n', 0) + 1
    print("Hello, {0}".format(app), datetime.now())


if __name__ == '__main__':
    app.run()
