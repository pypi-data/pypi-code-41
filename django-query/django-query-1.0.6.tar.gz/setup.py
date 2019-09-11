# -*- coding: utf-8 -*-
from __future__ import with_statement

from setuptools import setup


version = '1.0.6'


setup(
    name='django-query',
    version=version,
    keywords='Djagno Query POST GET',
    description='Get Django Query Values by POST/GET',
    long_description=open('README.rst').read(),

    url='https://github.com/Brightcells/django-query',

    author='Hackathon',
    author_email='kimi.huang@brightcells.com',

    packages=['django_query'],
    py_modules=[],
    install_requires=[],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Office/Business :: Financial :: Spreadsheet',
    ],
)
