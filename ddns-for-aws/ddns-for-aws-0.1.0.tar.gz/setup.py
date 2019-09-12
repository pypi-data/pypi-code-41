#!/bin/env/python3

from setuptools import setup, find_packages

with open('README.rst', encoding='UTF-8') as f:
    readme = f.read()

setup(
    name='ddns-for-aws',
    version='0.1.0',
    description='Syncs an A Record in Route53 with your external IP',
    long_description=readme,
    author='Ben Gardner',
    author_email='bgardner160@gmail.com',
    url='https://github.com/aDrongo/ddns-for-aws/',
    download_url='https://github.com/aDrongo/ddns-for-aws/archive/0.1.tar.gz',
    install_requires=['boto3'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'set-ddns=ddnsaws.ddnsaws:main',
            ]
        }
)
