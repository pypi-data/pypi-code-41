#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 Tongdun Inc. All Rights Reserved.
# @Time             : 2019/8/17 10:35 AM
# @Author           : ding
# @File             : demo_deploy.py
# @description      :

from tdserver import BaseHandler, BinaHandler, deploy


class DemoServer(BaseHandler):
    def algorithm(self, req, image):
        return self.build_resp((True, str(req)))


# you can use curl 0.0.0.0:8080/inference -F 'img_raw=@path_to_image'
class DemoBinaServer(BinaHandler):
    def algorithm(self, image):
        return BaseHandler.build_resp((True, str(image.shape)))


if __name__ == '__main__':
    deploy(8080, DemoBinaServer)
