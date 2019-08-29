from codecs import StreamReader, open
from distutils.version import LooseVersion
from os.path import dirname, join, realpath

from setuptools import setup
from setuptools.version import __version__

##
# Because of the way we declare dependencies here, we need a more recent
# version of setuptools.
# https://www.python.org/dev/peps/pep-0508/#environment-markers
if LooseVersion(__version__) < LooseVersion('20.5'):
    raise EnvironmentError('Django Filters requires setuptools 20.5 or later.')

##
# Load long description for PyPi.
readme = join(dirname(realpath(__file__)), 'README.rst')
with open(readme, 'r', 'utf-8') as f:  # type: StreamReader
    long_description = f.read()

##
# Off we go!
setup(
    name='phx-filters-django',
    description='Adds filters for Django-specific features.',
    url='https://filters.readthedocs.io/',

    version='2.0.0',

    packages=['filters_django'],

    # Install package filters into the global registry.
    entry_points={
        'filters.extensions': [
            'Model = filters_django:Model',
        ],
    },

    long_description=long_description,

    install_requires=[
        'Django >= 2.0',
        'phx-filters',
    ],

    extras_require={
        'test-runner': ['tox >= 3.7', 'django-nose'],
    },

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

    keywords='data validation, django',

    author='Phoenix Zerin',
    author_email='phx@phx.ph',
)
