#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: xiaoC
# Mail: i@xiaoc.cn
# Created Time:  2019-08-22 16:39:13
#############################################

from setuptools import setup, find_packages            #这个包没有的可以pip一下

setup(
    name = "cPython",      #这里是pip项目发布的名称
    version = "0.0.4",  #版本号，数值大的会优先被pip
    keywords = ("cPython"),
    description = "more common def",
    long_description = "more common def",
    license = "MIT Licence",

    url = "https://github.com/JxiaoC/cPython",     #项目相关文件地址，一般是github
    author = "xiaoC",
    author_email = "i@xiaoc.cn",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["pymongo", "requests"]          #这个项目需要的第三方库
)
