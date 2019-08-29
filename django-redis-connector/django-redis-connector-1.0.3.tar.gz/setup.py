# -*- coding: utf-8 -*-

from setuptools import setup


version = '1.0.3'


setup(
    name='django-redis-connector',
    version=version,
    keywords='Django Redis Connector',
    description='Django Redis Connector',
    long_description=open('README.rst').read(),

    url='https://github.com/django-xxx/django-redis-connector',

    author='Hackathon',
    author_email='kimi.huang@brightcells.com',

    packages=['django_redis_connector'],
    py_modules=[],
    install_requires=['redis-extensions'],

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
