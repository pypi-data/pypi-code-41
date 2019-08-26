# -*- coding: utf-8 -*-
"""
 @Time    : 19/7/29 11:15
 @Author  : CyanZoy
 @File    : setup.py.py
 @Software: PyCharm
 @Describe: 
 """
# !/usr/bin/env python


from setuptools import setup, find_packages

import drf_docs

setup(
    name="drf_docs",
    version=drf_docs.__version__,
    keywords=["pip", "api", "docs"],
    description="增加文档错误代码配置",
    long_description="django restframework api docs",
    license="MIT Licence",

    url="https://github.com/MAOA-L/docs_drf/tree/master/drf_docs",
    author="MAOA-L",
    author_email="chanzhouyun@gmail.com",

    packages=find_packages(),
    # include_package_data=True,
    # package_dir={'': ''},
    package_data={
        '': ['static/drf_docs/css/*', 'static/drf_docs/js/*', 'static/drf_docs/fonts/*', 'static/drf_docs/less/*', "templates/drf_docs/*.html"],
    },
    platforms="any",
    install_requires=['djangorestframework']
)