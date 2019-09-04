# -*- coding: utf-8 -*-

from setuptools import setup


version = '1.1.1'


setup(
    name='django-paginator2',
    version=version,
    keywords='Django Paginator Pagination',
    description='Simple Django Paginator',
    long_description=open('README.rst').read(),

    url='https://github.com/django-xxx/django-paginator',

    author='Hackathon',
    author_email='kimi.huang@brightcells.com',

    packages=['paginator'],
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
