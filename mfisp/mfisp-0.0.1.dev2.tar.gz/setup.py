# -*- coding: utf-8 -*-
"""
documentation
"""

from setuptools import setup, find_packages

setup(
    name='mfisp',
    version='0.0.1.dev2',
    description=
    'microfluidic image stack processing, currently contains two tools: for registration, for auto-rotation',
    long_description='see https://github.com/csachs/mfisp',
    author='Christian C. Sachs',
    author_email='sachs.christian@gmail.com',
    install_requires=['molyso', 'tifffile', 'mfisp-boxdetection'],
    url='https://github.com/csachs/mfisp',
    packages=find_packages(),
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3'
    ]
)
