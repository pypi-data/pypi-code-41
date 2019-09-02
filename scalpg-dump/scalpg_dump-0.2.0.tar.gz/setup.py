#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'dj_database_url',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='scalpg_dump',
    version='0.2.0',
    description="Dumps your Scalingo PostgreSQL database without the hustle",
    long_description=readme + '\n\n' + history,
    author="Tobias Englert",
    author_email='tobias@englert.it',
    url='https://github.com/tobiase/scalpg_dump',
    packages=[
        'scalpg_dump',
    ],
    package_dir={
        'scalpg_dump': 'scalpg_dump'
    },
    include_package_data=True,
    install_requires=requirements,
    entry_points='''
        [console_scripts]
        scalpg_dump=scalpg_dump.scalpg_dump:main
    ''',
    license="MIT license",
    zip_safe=False,
    keywords='scalpg_dump',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
