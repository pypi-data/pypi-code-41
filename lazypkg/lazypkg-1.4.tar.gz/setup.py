# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 16:17:00 2017

@author: Yoel Cortes-Pena
"""
from setuptools import setup

setup(
    name='lazypkg',
    packages=['lazypkg'],
    license='MIT',
    version='1.4',
    description='lazy import modules and subpackages',
    long_description=open('README.rst').read(),
    author='Yoel Cortes-Pena',
    install_requires=[],
    python_requires=">=3.6",
    package_data=
        {'lazypkg': [], },
    platforms=['Windows', 'Mac', 'Linux'],
    author_email='yoelcortes@gmail.com',
    url='https://github.com/yoelcortes/lazypkg',
    download_url='https://github.com/yoelcortes/lazypkg.git',
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Environment :: Console',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Topic :: Software Development :: Libraries :: Python Modules'],
    keywords='lazy import modules and subpackages package tools',
)