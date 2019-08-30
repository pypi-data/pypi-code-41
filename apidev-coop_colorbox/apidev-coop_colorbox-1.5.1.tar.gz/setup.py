#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages


VERSION = __import__('colorbox').__version__


setup(
    name='apidev-coop_colorbox',
    version=VERSION,
    description='Manage colorbox popup for django',
    long_description=open('README.rst').read(),
    packages=find_packages(),
    include_package_data=True,
    author='Luc Jean',
    author_email='ljean@apidev.fr',
    license='BSD',
    url="https://github.com/ljean/coop-colorbox/",
    download_url="https://github.com/ljean/coop-colorbox/tarball/master",
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'Natural Language :: English',
        'Natural Language :: French',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
)
