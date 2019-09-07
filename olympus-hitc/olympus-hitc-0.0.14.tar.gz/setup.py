#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: gaoyu
# Mail: v-yu.gao@horizon.ai
# Created Time:  2019-8-26
#############################################


from setuptools import setup, find_packages  
#这个包没有的可以pip一下

# with open('README.rst', encoding='UTF-8') as f:
#     long_description = f.read()

with open('LICENSE', encoding='UTF-8') as f:
    license = f.read()

setup(
    name = "olympus-hitc",      #这里是pip项目发布的名称
    version = "0.0.14",  #版本号，数值大的会优先被pip
    keywords = ["pip", "olympus","hitc"],
    description = "an api of project olympus",
    # long_description=readme,
    license = license,

    url = "http://gitlab.hobot.cc/ptd/ap/toolchain/ai-platform/olympus/tree/dev/python",     #项目相关文件地址，一般是github
    author = "gaoyu",
    author_email = "v-yu.gao@horizon.ai",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["requests"]          #这个项目需要的第三方库
)
