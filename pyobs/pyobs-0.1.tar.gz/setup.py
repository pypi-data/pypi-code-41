#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from distutils.core import setup
from setuptools.command.sdist import sdist

version = "0.1"

try:
    with open('README.md', 'r') as readme_file:
        description = readme_file.read()
except IOError:
    description = "Please take a look at the README.md"


# Generate classes
class UpdateClasses(sdist):
    def run(self):
        from os.path import dirname
        from sys import path
        path.append(dirname(__file__))
        from generate_classes import generate_classes
        generate_classes()
        sdist.run(self)


setup(
    name='pyobs',
    packages=['pyobs'],
    cmdclass={'sdist': UpdateClasses},
    license='MIT',
    version=version,
    description='Python library to communicate with an obs-websocket server.',
    long_description=description,
    long_description_content_type="text/markdown",
    author='Adrián "Adirio" Orive',
    author_email='adrian.orive.oneca@gmail.com',
    url='https://github.com/Adirio/pyobs',
    download_url='https://github.com/Adirio/pyobs/archive/{}.tar.gz'.format(
        version),
    keywords=['obs', 'obs-studio', 'websocket'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',

        'Development Status :: 4 - Beta',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=['websocket-client', 'six'],
)
