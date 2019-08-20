#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 Tongdun Inc. All Rights Reserved.
# @Time             : 2019/8/17 10:35 AM
# @Author           : ding
# @File             : demo_deploy.py
# @description      :

from tdserver import BaseHandler, deploy


class DemoHandler(BaseHandler):
    def algorithm(self, req):
        return self.build_resp((True, str(req)))


if __name__ == '__main__':
    deploy(8080, DemoHandler)
