# -*- coding: UTF-8 -*-

from setuptools import setup, find_packages
# or
# from distutils.core import setup
setup(
    name='toil-runner',     # 包名字
    version='1.2.4',   # 包版本
    description='This is a decorator of runner',   # 简单描述
    author='LongHui.Yin',  # 作者
    author_email='dragonfly.yin@genowis.com',  # 作者邮箱
    packages=find_packages(),                 # 包
    install_requires=['docker', 'wrapt', 'sarge']
)
