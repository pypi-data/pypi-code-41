#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: gaoyu
# Mail: xiangqukk@163.com
# Created Time:  2019-8-26
#############################################

from setuptools import setup, find_packages            #这个包没有的可以pip一下

setup(
    name = "test_upload_v1",      #这里是pip项目发布的名称
    version = "1.0.0",  #版本号，数值大的会优先被pip
    keywords = ["pip", "olympus","ffffff"],
    description = "an api of project olympus",
    long_description = "An api for olympus cmd ,that is a service for Programmer",
    license = "SMO Licence",

    url = "https://github.com/gggggaoyu/olympus",     #项目相关文件地址，一般是github
    author = "gaoyu",
    author_email = "xiangqukk@163.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["requests"]          #这个项目需要的第三方库
)
