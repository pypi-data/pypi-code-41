#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys
import os

here = os.path.abspath(os.path.dirname(__file__))
py_version = sys.version_info[:2]

if py_version <= (2, 7):
    raise RuntimeError('On Python 2, Oracle not Support !')
elif (3, 0) < py_version < (3, 6):
    raise RuntimeError('On Python 3, Oracle requires Python 3.6 or later')

try:
    README = open(os.path.join(here, 'README.md')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except:
    README = """
oracle 是一个智能协约的管理程序，用于导入event的数据到数据库中，和处理event数据
"""
    CHANGES = ''


setup(
    name="pycontractsdk.v2",
    version="0.1.1",
    author="yuyongpeng",
    author_email="yuyongpeng@hotmail.com",
    description=("This is a sdk of constract"),
    # long_description=README + '\n\n' + CHANGES,
    # long_description_markdown_filename='README.md',
    license="MIT",
    keywords="solidity web3 constract sdk",
    url="https://github.com/yuyongpeng/pyconstractsdk",
    # packages=['pycontractsdk'],  # 需要打包的目录列表
    packages = find_packages(where='.', exclude=('tests', 'tests.*'), include=('*',)),
    # 需要安装的依赖
    install_requires=[
        'web3==4.8.3',
        'ethereum==2.3.2',
        'eth-account==0.3.0',
        'eth-utils==1.4.1',
        'eth-keys==0.2.1',
        'eth-abi==1.3.0',
        'eth-keyfile==0.5.1',
        'eth-hash==0.2.0',
        'arrow==0.13.1',
        'logbook==1.4.4',
        'py-solc==3.2.0',
    ],
    py_modules=['pycontractsdk'],
    python_requires='>=3.6',
    setup_requires=['setuptools-markdown'],
    # 添加这个选项，在windows下Python目录的scripts下生成exe文件
    # 注意：模块与函数之间是冒号:
    entry_points={'console_scripts': [
    ]},

    # long_description=read('README.md'),
    classifiers=[  # 程序的所属分类列表
        "Development Status :: 3 - Alpha",
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Topic :: Utilities",
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
    ],
    zip_safe=False
)

