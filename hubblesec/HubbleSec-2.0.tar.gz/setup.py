# -*- coding: UTF-8 -*-
from setuptools import setup

from setuptools import setup, find_packages

# with open("README.md", "r",encoding='GBK') as fh:
#     long_description = fh.read()

setup(
    name='HubbleSec',
    version='2.0',
    description='python library for Guanxing',
    author='AJay13',
    author_email='1599121712@qq.com',
    url='https://github.com/Hatcat123/HubbleSec',
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    # py_modules=['gxscan.gxscan'],
    # packages=['demo3','demo2.config'],
    packages=find_packages(),
    install_requires =[
        'requests',
        'python-socketio',
        'SQLAlchemy',
        'urllib3',
        'geoip2',
    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)