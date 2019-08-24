#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['troposphere>=2.5.0' ]

setup_requirements = ['pytest-runner']

test_requirements = ['pytest']

setup(
    author="John Mille",
    author_email='JohnPreston@users.noreply.github.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="CFN Macro Common Lib",
    entry_points={
        'console_scripts': [
            'cfn_macro_common=cfn_macro_common.cli:main',
        ],
    },
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='cfn_macro_common',
    name='cfn_macro_common',
    packages=find_packages(include=['cfn_macro_common']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/johnpreston/cfn_macro_common',
    version='0.1.0',
    zip_safe=False,
)
