#!/usr/bin/env python
#-*- coding:utf-8 -*-

from setuptools import setup, find_packages

setup(
    name = "swdclient",
    version = "0.1.0",
    keywords = ("pip", "iscas","auto",),
    description = "SafeWorking Drive Client SDK",
    long_description = "SafeWorking Drive Client SDK",
    license = "MulanPSL",

    url = "http://evaluateai.cn/",
    author = "yangguang",
    author_email = "yangguang@iscas.ac.cn",

    packages = find_packages(),
    include_package_data = True,
    platforms = "linux",
    install_requires = []
)