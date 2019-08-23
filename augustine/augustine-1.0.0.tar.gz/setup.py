# coding=utf-8
from setuptools import find_packages, setup


setup(
    name='augustine',
    version='1.0.0',
    packages=find_packages(),
    author='Michael Brennan',
    author_email='michael@michaelbrennan.net',
    description='Tools for creating Python packages',
    keywords='package tools',
    url='https://github.com/mbrennan/augustine',
    package_data={'': ['data/*']},
    install_requires=['setuptools', 'typing'],
    extras_require=dict(
        color=['colorama', 'termcolor'],
        run_command=['gevent']),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
