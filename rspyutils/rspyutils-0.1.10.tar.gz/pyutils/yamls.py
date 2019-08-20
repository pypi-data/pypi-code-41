# !/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created on MAY 21, 2018
@author: zhanglanhui
homepage recommender:ffm
"""
import yaml


def read_from_yaml(file: str) -> dict:
    with open(file) as f:
        conf_dic = yaml.load(f.read(), Loader=yaml.FullLoader)
    return conf_dic


def get_str(file: str, key: str) -> dict:
    conf_dic = read_from_yaml(file)
    return conf_dic.get(key, "")


if __name__ == "__main__":
    print(read_from_yaml("config/dev/server_config.yaml"))
