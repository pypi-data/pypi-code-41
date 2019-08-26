from setuptools import setup, find_packages
import re
import os

# Get package name from directory
name = os.path.basename(os.path.dirname(os.path.realpath(__file__)))

# Read version from __init__.py
with open('{}/__init__.py'.format(name), 'r') as file:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        file.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setup(name             = name,
      version          = version,
      author           = 'Logan Grado',
      author_email     = 'grado.logan@gmail.com',
      description      = 'Tucker Davis Technologies tools',
      license          = '',
      url              = '',
      packages         = find_packages(),
      install_requires = ['numpy',
                          'tabulate']
)
