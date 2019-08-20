#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os

from setuptools import setup, find_packages
setup(
    name = "rest_framework_swagger_zl",
    version = "0.0.4",
    keywords = ("pip", "rest_framework_swagger_zl"),
    description = "generate api doc html,Swagger UI for Django REST Framework 3.5+",
    long_description = "generate api doc html,Swagger UI for Django REST Framework 3.5+",
    license='FreeBSD License',
    url = "https://github.com/zhangliu520/rest_framework_swagger_zl.git",
    author = "mrzl",
    author_email = "752477168@qq.com",
    packages = find_packages(),
    include_package_data=True,
    platforms = "any",
    install_requires = [],

)

