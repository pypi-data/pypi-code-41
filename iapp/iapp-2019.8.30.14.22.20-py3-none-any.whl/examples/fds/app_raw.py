#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : app_raw
# @Time         : 2019-08-30 14:15
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 


from sanic import Sanic, response

app = Sanic()


@app.route('/')
async def index(request):
    return response.text("OK")



app.run(debug=True)