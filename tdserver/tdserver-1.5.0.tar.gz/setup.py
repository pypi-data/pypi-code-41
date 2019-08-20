#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 Tongdun Inc. All Rights Reserved.
# @Time             : 2019/8/16 4:16 PM
# @Author           : ding
# @File             : setup.py
# @description      :

from distutils.core import setup
from setuptools import find_packages


setup(name='tdserver',  # 包名
      version='1.5.0',  # 版本号
      description='dddz.cvding\'s tdserver',
      long_description='using tornado to deploy Image Sever and Get result from Server URL',
      author='dddz',
      author_email='cvchina@163.com',
      url='',
      license='',
      install_requires=["opencv-python", "requests", "numpy", "tornado"],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Utilities'
      ],
      keywords='',
      packages=find_packages('src'),  # 必填
      package_dir={'': 'src'},  # 必填
      include_package_data=True,
      scripts=['scripts/demo_proc.py', 'scripts/demo_deploy.py'],
      )
