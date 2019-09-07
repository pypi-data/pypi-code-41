# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-website-coverpage',
    version='0.0.12',
    author=u'Jon Combe',
    author_email='pypi@joncombe.net',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    url='https://github.com/joncombe/django-website-coverpage',
    license='BSD licence, see LICENCE file',
    description='Easy website coverpages for Django',
    long_description='Easy website coverpages for Django',
    zip_safe=False,
)
