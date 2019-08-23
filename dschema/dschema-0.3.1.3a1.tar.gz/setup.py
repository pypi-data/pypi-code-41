#! /usr/bin/env python3

from setuptools import setup, find_packages
import re

version = ''
with open('dschema/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')


readme = ''
with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()


setup(name='dschema',
      python_requires='>=3.4',
      author='Teriks',
      author_email='Teriks@users.noreply.github.com',
      url='https://github.com/Teriks/dschema',
      version=version,
      packages=find_packages(exclude=('tests',)),
      license='BSD 3-Clause',
      description='Python dictionary validation by schema.',
      long_description=readme,
      include_package_data=True,
      install_requires=[],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: BSD License',
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Software Development :: Libraries',
      ]
)