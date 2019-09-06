#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='HanhanAI',
    version='1.0.0',
    description=
        'Universal game AI system for game developer',
    long_description=open('README.rst').read(),
    author='HanhanAI producer1',
    author_email='1379612504@qq.com',
    maintainer='HanhanAI producer2',
    maintainer_email='762613908@qq.com',
    license='MIT',
    packages=['HanhanAI'],
    platforms=["all"],
    url='https://github.com/hanhan-ai/2019HanHan',#github网址
    install_requires=[ 'keras>=2.2.5','numpy>=1.17.0','matplotlib>=3.1.1'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: Chinese (Simplified)',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Topic :: Adaptive Technologies'
    ],
)
