#!/usr/bin/env python 
# -*- coding:utf-8 -*-
############################
#File Name: setup.py
#Author: ykyk
#Mail: 525178992@qq.com
#Created Time: 2019-09-07 12:55:39
############################

try:
    from setuptools import setup, find_packages
except:
    from distutils.core import setup
from codecs import open
from os import path

#版本号
VERSION = '0.0.1'

#发布作者
AUTHOR = "yhkl"

#邮箱
AUTHOR_EMAIL = "kaiyang939325@gmail.com"

URL = "https://github.com/yhkl-dev/yamlpars"

#项目名称
NAME = "yamlparse"

#项目简介
DESCRIPTION = "命令解析yaml文件并替换键值 工具"

#LONG_DESCRIPTION为项目详细介绍，这里取README.md作为介绍
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

#搜索关键词
KEYWORDS = "yaml parse"

#发布LICENSE
LICENSE = "MIT"

#包
PACKAGES = ["ymlparse"]

#具体的设置
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',

    ],
    #指定控制台命令
    entry_points={
        'console_scripts': [
            'yamlparse = ymlparse.parse_yaml:main',
        ],
    },
    keywords=KEYWORDS,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    packages=PACKAGES,
    install_requires=['argparse', 'pyyaml'],#依赖的第三方包
    include_package_data=True,
    zip_safe=True,
)

