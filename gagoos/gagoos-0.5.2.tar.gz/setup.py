#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# IDE: PyCharm 2017.2.4
# Author: Dajiang Ren<rendajiang@gagogroup.com>
# Created on 2018-09-26


from distutils.core import setup #如果没有需要先安装


setup(
    name='gagoos',  #打包后的包文件名
    version='0.5.2',  #版本
    description='Gago Object Storage',
    author='rockdj1983',
    author_email='rockdj1983@163.com',
    url='http://www.gagogroup.cn',
    packages=['gagoos'],  #与前面的新建文件名一致
    install_requires=[
        'boto3',
        'botocore',
        'oss2'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
