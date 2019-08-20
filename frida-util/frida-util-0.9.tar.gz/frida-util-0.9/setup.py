# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
import os, sys, ast

here = os.path.abspath(os.path.dirname(__file__))
version = '0.9'

#with open(path.join(here, 'README.md'), encoding='utf-8') as f:
#    long_description = f.read()
long_description = "Now called 'revenge'"

# Frida 12.6.11 -> https://github.com/frida/frida/issues/986

setup(
    name='frida-util',
    version=version,
    description='REVerse ENGineering Environment',
    long_description=long_description,
    url='https://github.com/bannsec/revenge',
    author='Michael Bann',
    author_email='self@bannsecurity.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX :: Linux',
        'Environment :: Console'
    ],
    keywords='frida python3 reversing dbi',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['revenge'],
)

