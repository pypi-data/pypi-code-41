#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['escam_toolbox==1.0.3', ]

setup_requirements = []

test_requirements = []

setup(
    author="Ralph Brecheisen",
    author_email='r.brecheisen@maastrichtuniversity.nl',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Tool for selecting and saving individual slices in a DICOM scan",
    entry_points={
        'console_scripts': [
            'escam_sliceselector=escam_sliceselector.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='escam_sliceselector',
    name='escam_sliceselector',
    packages=find_packages(include=['escam_sliceselector']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/rbrecheisen/escam_sliceselector',
    version=open('VERSION', 'r').readline(),
    zip_safe=False,
)
