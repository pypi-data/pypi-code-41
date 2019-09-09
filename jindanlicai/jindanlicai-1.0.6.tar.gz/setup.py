from __future__ import print_function
from setuptools import setup, find_packages
import sys

with open("README.md", "r") as fh:
    long_description = fh.read()
setup(
    name="jindanlicai",
    version="1.0.6",
    author="WEI HAITONG",
    author_email="loveweihaitong@foxmail.com",
    description="A Python library for downloading YouTube videos.",
    long_description=long_description,
    license="MIT",
    url="https://github.com/messliu/jindanlicai.git",
    packages=['jindanlicai'],
    classifiers=[
        "Environment :: Web Environment",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Topic :: Multimedia :: Video',
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=True,
)
