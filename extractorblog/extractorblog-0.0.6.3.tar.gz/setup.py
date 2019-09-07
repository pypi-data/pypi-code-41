# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

__author__ = 'JacksonSun'
__date__ = '2019/03/11'


setup(
    name='extractorblog',                                # 名称
    version='0.0.6.3',                                 # 版本号
    description='extractor blog',                          # 简单描述
    # long_description=long_description,               # 详细描述
    # long_description_content_type='text/markdown',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    keywords='blog extractor text keywords',                 # 关键字
    author='JacksonSun',                               # 作者
    author_email='jacksonsunjj@gmail.com',                # 邮箱
    url='https://github.com/SunJackson/extractor-blog',      # 包含包的项目地址
    license='MIT',                                  # 授权方式
    packages=find_packages(),                       # 包列表
    install_requires=[
        'requests',
        'chardet',
        'beautifulsoup4'
    ],
    include_package_data=True,
    zip_safe=True,

)
