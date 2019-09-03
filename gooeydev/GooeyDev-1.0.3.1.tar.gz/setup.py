"""Script for setuptools."""
import sys
from setuptools import setup, find_packages


with open('README.md') as readme:
    long_description = readme.read()

version = '1.0.3.1'

deps = [
    'Pillow>=4.3.0',
    'psutil>=5.4.2',
    'colored>=1.3.93'
]

if sys.version[0] == '3':
    deps.append('wxpython>=4.0.2')


setup(
    name='GooeyDev',
    version=version,
    url='',
    author='Thorsten Wagner',
    author_email='thorsten.wagner@mpi-dortmund.mpg.de',
    description=('Gooey (made by Chris Kiehl) turns (almost) any command line program into a full GUI '
                 'application with one line. This a custom release of the development branch (1.0.3) of gooey.'),
    license='MIT',
    packages=find_packages(),
    install_requires=deps,
    include_package_data=True,
    dependency_links = ["http://www.wxpython.org/download.php"],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Desktop Environment',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Widget Sets',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'
    ],
    long_description='''

Gooey (Beta)
############


This a custom release of the development branch (1.0.3) of gooey.

_'''
)
