#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='comk_utils',  # 包名
    version='1.0.7',  # 版本
    description=(  # 简述
        'comk个人开发的小工具集合，不断更新中。'
    ),
    long_description=open('README.rst', encoding='utf-8').read(),  # 长描述， 必须是rst（reStructuredText )格式的，
    author='comk',  # 作者
    author_email='1943336161@qq.com',  # 作者邮箱
    maintainer='comk',  # 维护人
    maintainer_email='1943336161@qq.com',  # 维护人邮箱
    license='BSD License',  # 协议
    packages=find_packages(),  # 申明你的包里面要包含的目录，可以让setuptools自动决定要包含哪些包
    platforms=["all"],
    url=None,  # 项目的网址，一般都是github的url
    classifiers=[  # 运行环境
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[  # 依赖包，安装包时pip会自动安装
        'xmltodict',
        'xlrd',
        'xlwt',
        'redis',
        'alipay-sdk-python',
    ]
)
