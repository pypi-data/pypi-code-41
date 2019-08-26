#!/usr/bin/python
# -*- coding: UTF-8 -*-

#-printtest
#--__init__.py
#--print1.py
#--print2.py

# import printtest 使用
# python setup.py sdist bdist_wheel              打包
# python -m twine upload --repository-url https://upload.pypi.org/legacy/  dist/*   上传网站
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dectyptmodel-dragonfly",
    version="0.0.1",
    author="dragonfly.Lu",
    author_email="329964085@qq.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)