# !/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@version: 0.1
@author: gabriel
@file: sentrys.py
@time: 2018/11/20 15:12
"""
from raven import Client
from pyutils.yamls import read_from_yaml


class SentryCli(object):
    def __init__(self, config_file, section="Sentry_dsn"):
        config = read_from_yaml(config_file)
        try:
            self.client = Client(config.get(section))
        except:
            raise Exception("Sentry_dsn input error!!!")

    def check_commom_err(self, e):
        self.client.captureException(e)
