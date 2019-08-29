from codecs import StreamReader, open
from os.path import dirname, join, realpath

from setuptools import setup

cwd = dirname(realpath(__file__))

##
# Load long description for PyPi.
with open(join(cwd, 'README.rst'), 'r', 'utf-8') as f:  # type: StreamReader
    long_description = f.read()

##
# Off we go!
setup(
    name='phx-filters-iso',
    description='Adds filters for interpreting ISO codes.',
    url='https://filters.readthedocs.io/',

    version='2.0.0',

    packages=['filters_iso'],

    # Install package filters into the global registry.
    entry_points={
        'filters.extensions': [
            'Country = filters_iso:Country',
            'Currency = filters_iso:Currency',
            'Locale = filters_iso:Locale',
        ],
    },

    long_description=long_description,

    install_requires=[
        'phx-filters',
        'iso3166',
        'language_tags',
        'py-moneyed',
    ],

    extras_require={
        'test-runner': ['tox >= 3.7'],
    },

    test_suite='test',
    test_loader='nose.loader:TestLoader',
    tests_require=[
        'nose',
    ],

    license='MIT',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Filters',
    ],

    keywords=
    'data validation, iso-3166, iso-4217, ietf language tags, bcp 47',

    author='Phoenix Zerin',
    author_email='phx@phx.ph',
)
