#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: Marj
# Mail: 598175639@qq.com
# Created Time:  2019-09-05 16:36:34
#############################################

from setuptools import setup, find_packages

setup(
    name = "SBTools",
    version = "0.0.5", 
    keywords = ("pip", "SBTools","sbtools"),
    description = "工具箱",
    long_description = "懒人工具箱",
    license = "MIT Licence",

    url = "",
    author = "Marj",
    author_email = "598175639@qq.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["requests","pymysql"]
)