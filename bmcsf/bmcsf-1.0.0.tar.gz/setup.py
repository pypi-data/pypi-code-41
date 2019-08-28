#!/usr/bin/env python

import setuptools

setuptools.setup(
    name='bmcsf',
    version='1.0.0',
    author='Berke Emrecan Arslan',
    author_email='berke@beremaran.com',
    description='Up/Down Minecraft Server on Vultr Fast',
    keywords='minecraft server vultr',
    url='https://github.com/beremaran/mcsf',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    install_requires=[
        'asn1crypto',
        'bcrypt',
        'certifi',
        'cffi',
        'chardet',
        'cryptography',
        'idna',
        'paramiko',
        'pkg-resources',
        'pycparser',
        'PyNaCl',
        'requests',
        'six',
        'urllib3',
        'vultr'
    ],
    scripts=[
        'bin/bmcsf'
    ]
)
