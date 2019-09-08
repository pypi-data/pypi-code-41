#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import sys
from setuptools import setup

platform = sys.platform
print(platform)

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = [
        'Click>=6.0',
        'bert-serving-server>=1.9.6',
        'bert-serving-client>=1.9.6',
        'flask',
        'flask_restplus',
        'numpy>=1.16.4',
        'tensorflow>=1.13',
        'tensorflow_hub>=0.5.0',
        'google-cloud-storage',
        'sentencepiece',
        'tf-sentencepiece',
        'pytorch-transformers',
        'python-telegram-bot>=12.0.0b1',
        'keras>=2.2.5',
        'Pillow',
        'hawking_proto']

setup_requirements = ['pytest-runner']

test_requirements = ['pytest']

setup(
    author="Peach Inc",
    author_email='hi@peach.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Operating System :: POSIX :: Linux",
        'Programming Language :: Python :: 3.6',
        "License :: OSI Approved :: Apache Software License"
    ],
    description="Hawking CLI",
    entry_points={
        'console_scripts': [
            'hawking=hawking.cli:main',
        ],
    },
    install_requires=requirements,
    keywords='hawking',
    name='hawking',
    packages=[
        'hawking',
        'hawking.encoder',
        'hawking.encoder.bert',
        'hawking.encoder.universal',
        'hawking.encoder.vgg',
        'hawking.encoder.resnet50',
        'hawking.encoder.inceptionresnetv2',
        'hawking.common',
        'hawking.serve',
        'hawking.frontend',
        'hawking.frontend.store',
        'hawking.frontend.api',
        'hawking.frontend.engine',
        'hawking.bot.telegram',
        'hawking.bot.secretary',
        'hawking.frontend'
    ],
    include_package_data=True,
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://www.peach.co',
    version='0.1.55',
    zip_safe=False,
    license='Apache License, Version 2.0'
)
