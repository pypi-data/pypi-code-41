#!/usr/bin/env python
from setuptools import setup, find_packages
import os
import sys

VERSION = '0.1.2'
# LONG_DESCRIPTION = open('intro.rst', 'r').read()

long_description = "\n".join([
    open('intro.rst', 'r').read(),
])

INSTALL_REQUIRES = [
    'Django',
    'pillow'
]

if sys.argv[-1] == 'build':
    os.system('rm -rf build dist *.egg-info')
    os.system('python setup.py sdist bdist_wheel')
    sys.exit()

if sys.argv[-1] == 'clear':
    os.system('rm -rf build dist *.egg-info django.log')
    sys.exit()

if sys.argv[-1] == 'publish':
    os.system('rm -rf build dist *.egg-info django.log')
    os.system('python setup.py sdist bdist_wheel')
    os.system('twine upload dist/*')
    sys.exit()

if sys.argv[-1] == 'tag':
    os.system("git tag -a %s -m 'version %s'" % (VERSION, VERSION))
    os.system("git push --tags")
    sys.exit()

setup(
    name='qitian-simditor',
    version=VERSION,
    description='Django admin Simditor integration. edit with ',
    long_description=long_description,
    author='Peter',
    author_email='peter@qitian.biz',
    url='https://gitee.com/qtch/django-simditor.git',
    zip_safe=False,
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(exclude=[".DS_Store", "app", "simditor_demo", "templates"]),
    keywords='Django admin Simditor integration!',
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ]
)
