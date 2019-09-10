#!python
# -*- coding:utf-8 -*-
from __future__ import print_function
from setuptools import setup, find_packages
import cubetranslate

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="cubetranslate",
    version='0.0.1',
    author="xuzl71",
    author_email="xuzlfight@qq.com",
    description="try how to upload pip package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="http://www.renren.com/u/1f4a7323",
    packages=find_packages(),
    install_requires=[
        "acumos",
        ],
    classifiers=[
        "Topic :: Artistic Software",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)