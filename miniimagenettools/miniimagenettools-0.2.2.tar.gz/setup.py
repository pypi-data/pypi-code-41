#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name='miniimagenettools',
    version='0.2.2',
    author='yaoyaoliu',
    author_email='yaoyaoliu@outlook.com',
    url='https://mtl.yyliu.net',
    description=u'Tools for generating mini-ImageNet dataset and processing batches',
    packages=['miniimagenettools'],
    install_requires=[
   'opencv-python',
   'numpy',
   'pillow',
   'tqdm'
]
)