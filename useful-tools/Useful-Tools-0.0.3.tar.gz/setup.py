# !usr\bin\env python
# -*- coding:utf-8 -*-
from setuptools import setup

setup(
    name='Useful-Tools',
    version='0.0.3',
    author='zltzlt',
    author_email='1668151593@qq.com',
    url='https://github.com/zhangletao/Tools',
    description='Some useful tools.',
    long_description='',
    packages=['Tools', 'Tools/Common', 'Tools/Files', 'Tools/Math'],
    install_requires=['pywin32', 'PyPDF2'])
