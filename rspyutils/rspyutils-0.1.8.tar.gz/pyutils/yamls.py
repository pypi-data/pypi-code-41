# !/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created on MAY 21, 2018
@author: zhanglanhui
homepage recommender:ffm
"""
import yaml


def read_from_yaml(file: str) -> dict:
    conf_dic = yaml.load(open(file, 'r'),
                         Loader=yaml.FullLoader)

    return conf_dic


if __name__ == "__main__":
    print(read_from_yaml("config/dev/server_config.yaml"))
