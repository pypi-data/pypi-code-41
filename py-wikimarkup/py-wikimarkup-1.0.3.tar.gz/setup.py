#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='py-wikimarkup',
    version='1.0.3',
    packages=find_packages(),
    description='A basic MediaWiki markup parser.',
    long_description=open('README.rst').read(),
    author='David Cramer',
    author_email='dcramer@gmail.com',
    url='http://www.github.com/dgilman/py-wikimarkup/',
    zip_safe=False,
    include_package_data=True,
    install_requires=['bleach>=2.0.0,<3.0.0'],
    package_data = { '': ['README.rst'] },
    python_requires='<3.0',
    classifiers=[
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Text Processing :: Markup',
        'Development Status :: 6 - Mature',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    ]
)
