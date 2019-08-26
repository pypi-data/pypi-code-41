#!/usr/bin/env python
from distutils.core import setup

setup(
    name='mobilelean-pypdftk',
    description='''Python wrapper for PDFTK''',
    version='0.4',
    author='Julien Bouquillon',
    author_email='julien@revolunet.com',
    url='http://github.com/MobileLean/pypdftk',
    py_modules=['pypdftk'],
    scripts=['pypdftk.py'],
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Web Environment',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Utilities'],
)
