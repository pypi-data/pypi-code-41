"""Setuptools entry point."""
import codecs
import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules'
]

dirname = os.path.dirname(__file__)

long_description = (
    codecs.open(os.path.join(dirname, 'README.rst'), encoding='utf-8').read() + '\n' +
    codecs.open(os.path.join(dirname, 'CHANGES.rst'), encoding='utf-8').read()
)

setup(
    name='go-pypi',
    version='0.0.1',
    description='Go pypi',
    long_description=long_description,
    author='Lu Aifei',
    author_email='luaf2008@qq.com',
    url='https://github.com/TechOpsX/go-pypi',
    packages=find_packages(),
    install_requires=[],
    classifiers=CLASSIFIERS)
