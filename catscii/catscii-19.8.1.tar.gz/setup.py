from setuptools import setup

__version__ = '19.8.1'
__author__ = 'R. THOMAS'
__licence__ = 'GPLv3'
__credits__ = "Romain Thomas"
__maintainer__ = "Romain Thomas"
__website__ = 'https://github.com/astrom-tom/catscii'
__email__ = "the.spartan.proj@gmail.com"
__status__ = "released"
__year__ = '2018-19'

setup(
   name = 'catscii',
   version = __version__,
   author = __credits__,
   packages = ['catscii'],
   description = 'A simple catalog query tool in python',
   python_requires = '>=3.6',
   install_requires = [
       "numpy >= 1.16",
   ],
   include_package_data=True,
)
