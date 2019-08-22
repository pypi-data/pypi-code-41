#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

import configparser
from goss.app import utils


class Config():
    def __init__(self, filename=None):
        self.filename = filename

        self.config = configparser.ConfigParser()
        if filename:
            self.config.read(filename)

    def get_value(self, section, name):
        '''获取值'''

        if section not in self.config:
            return None

        sec = self.config[section]

        if name not in sec:
            return None

        return sec[name]


goss_config = Config(utils.GOSS_CONFIG_PATH)

class ConfigParser():
    def __init__(self, *filenames):
        self._conf = configparser.ConfigParser()
        self._conf.read(filenames)

    def read(self, *conf_path):
        self._conf.read(conf_path)

    def __getattr__(self, name):
        if name in self._conf.sections():
            return self.Section(self._conf[name])
        return self.Section()

    class Section():
        def __init__(self, sec={}):
            self.sec = sec

        def __getattr__(self, name):
            return self.sec.get(name)

if __name__ == "__main__":
    c = ConfigParser('/Users/wxnacy/.config/goss/credentials',
            '/Users/wxnacy/.config/goss/config')
    print(c.user)
    print(c.user.name)

