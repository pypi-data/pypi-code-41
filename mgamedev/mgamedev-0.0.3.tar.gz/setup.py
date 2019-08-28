#!/usr/bin/env python
# -*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: LiangjunFeng
# Mail: zhumavip@163.com
# Created Time:  2018-4-16 19:17:34
#############################################

from setuptools import setup, find_packages  # 这个包没有的可以pip一下
import json
import shutil

confdic = dict()
with open("conf.json", "r") as fp:
    cont = fp.read()
    confdic = json.loads(cont)

shutil.rmtree("./dist")

setup(
    name=confdic["name"],  # 这里是pip项目发布的名称
    version=confdic["version"],  # 版本号，数值大的会优先被pip
    keywords=("dwb"),
    description="Private tools for develop mobile client games",
    long_description="All is poor extension!Don't use!",
    license="Mozilla Licence",

    url="https://gitee.com/heyzf/pytools_2dx",  # 项目相关文件地址，一般是github
    author="dwb",
    author_email="dwb@dwb.ren",

    packages=find_packages(),
    include_package_data=True,
    package_dir=[],
    install_requires=[]  # 这个项目需要的第三方库
)