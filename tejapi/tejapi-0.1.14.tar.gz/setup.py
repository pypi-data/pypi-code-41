# coding=UTF-8
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

install_requires = [
    'pandas >= 0.18.1',
    'numpy >= 1.8',
    'requests >= 2.7.0',
    'inflection >= 0.3.1',
    'python-dateutil',
    'six',
    'more-itertools'
]

installs_for_two = [
    'pyOpenSSL',
    'ndg-httpsclient',
    'pyasn1'
]

if sys.version_info[0] < 3:
    install_requires += installs_for_two

packages = [
    'tejapi',
    'tejapi.errors',
    'tejapi.model',
    'tejapi.operations',
    'tejapi.utils'
]

setup(
    name='tejapi',
    description='Package for access tej database from REST API',
    keywords=['tej', 'API', 'data', 'financial', 'economic'],
    long_description='A Python library for TEJ RESTful API.  For more information, please access https://api.tej.com.tw .',
    version='0.1.14',
    author='tej',
    author_email='tej@tej.com.tw',
    maintainer='tej api Development Team',
    maintainer_email='tej@tej.com',
    url='https://api.tej.com.tw',
    license='MIT',
    install_requires=install_requires,
    tests_require=[
        'unittest2',
        'flake8',
        'nose',
        'httpretty',
        'mock',
        'factory_boy',
        'jsondate'
    ],
    test_suite="nose.collector",
    packages=packages
)