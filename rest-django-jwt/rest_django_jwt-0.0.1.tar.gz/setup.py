# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     setup
   Description :
   Author :       jusk?
   date：          2019/8/31
-------------------------------------------------
   Change Activity:
                   2019/8/31:
-------------------------------------------------
"""


from setuptools import setup, find_packages

setup(
    name = "rest_django_jwt",
    version = "0.0.1",
    keywords = ("pip", "datacanvas", "eds", "xiaoh"),
    description = "eds sdk",
    long_description = "eds sdk for python",
    license = "MIT Licence",

    url = "http://xiaoh.me",
    author = "xiaoh",
    author_email = "huoxingming@gmail.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ['requests']
)