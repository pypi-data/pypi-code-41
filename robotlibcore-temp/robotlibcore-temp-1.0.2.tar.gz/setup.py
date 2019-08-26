#!/usr/bin/env python

from os.path import abspath, join, dirname
from setuptools import find_packages, setup


CURDIR = dirname(abspath(__file__))

with open(join(CURDIR, 'src', 'robotlibcore', 'version.py')) as f:
    exec(f.read())
    VERSION = get_version()
with open(join(CURDIR, 'README.rst')) as f:
    LONG_DESCRIPTION = f.read()
    """
    base_url = 'https://github.com/robotframework/PythonLibCore/blob/master'
    for text in ('INSTALL', 'CONTRIBUTING'):
        search = '`<{0}.rst>`__'.format(text)
        replace = '`{0}.rst <{1}/{0}.rst>`__'.format(text, base_url)
        if search not in LONG_DESCRIPTION:
            raise RuntimeError('{} not found from README.rst'.format(search))
        LONG_DESCRIPTION = LONG_DESCRIPTION.replace(search, replace)
    """
CLASSIFIERS = """
Development Status :: 5 - Production/Stable
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Programming Language :: Python :: 2
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: Implementation :: CPython
Programming Language :: Python :: Implementation :: Jython
Programming Language :: Python :: Implementation :: IronPython
Programming Language :: Python :: Implementation :: PyPy
Topic :: Software Development :: Testing
Topic :: Software Development :: Testing :: Acceptance
Topic :: Software Development :: Testing :: BDD
Framework :: Robot Framework
""".strip().splitlines()
DESCRIPTION = ('Tools to ease creating larger test libraries for Robot Framework using Python.')
KEYWORDS = ('robotframework automation libraries')

setup(
    name         = 'robotlibcore-temp',
    version      = VERSION,
    author       = u'Pekka Kl\xe4rck',
    author_email = 'peke@eliga.fi',
    url          = 'http://robotframework.org',
    download_url = 'https://pypi.python.org/pypi/robotframework',
    license      = 'Apache License 2.0',
    description  = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    keywords     = KEYWORDS,
    platforms    = 'any',
    classifiers  = CLASSIFIERS,
    package_dir  = {'': 'src'},
    packages     = find_packages('src')
)
