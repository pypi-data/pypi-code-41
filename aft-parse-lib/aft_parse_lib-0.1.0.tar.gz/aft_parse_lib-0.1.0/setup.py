#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time: 2019-08-22 16:29
# @Author: xiaopeng

from setuptools import setup, find_packages            #这个包没有的可以pip一下

setup(
    name = "aft_parse_lib",      #这里是pip项目发布的名称
    version = "0.1.0",  #版本号，数值大的会优先被pip
    keywords = ("pip", "aft-parse-lib", "parseutil"),
    description = "An util of parsing",
    long_description = "An util of parsing, from origin to viewable",
    license = "MIT Licence",

    url = "https://github.com/LiangjunFeng/SICA",
    author = "Xiaopeng",
    author_email = "isharpener@163.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["requests", "pymysql", "DBUtils", "afanti_tiku_lib"]          #这个项目需要的第三方库
)