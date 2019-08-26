#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='semantic_segmentation',
    version='0.0.5',
    description=(
        'Semantic Segmentation on Tensorflow && Keras'
    ),
    long_description=open('README.MD').read(),
    long_description_content_type='text/markdown',
    author='Yang Lu',
    author_email='luyanger1799@outlook.com',
    license='Apache 2,0 License',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/luyanger1799/Amazing-Semantic-Segmentation.git',
    python_requires='>=3.6',
    )