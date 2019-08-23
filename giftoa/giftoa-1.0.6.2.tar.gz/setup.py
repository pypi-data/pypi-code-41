#! /usr/bin/env python3

from setuptools import setup, find_packages
import re

version = ''
with open('giftoa/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')


readme = ''
with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()


setup(name='giftoa',
      author='Teriks',
      author_email='Teriks@users.noreply.github.com',
      url='https://github.com/Teriks/giftoa',
      version=version,
      packages=find_packages(exclude=("debian_packaging",)),
      license='BSD 3-Clause',
      description='Python script which compiles a native binary that plays a GIF in ASCII on the terminal using ncurses.',
      long_description=readme,
      include_package_data=True,
      install_requires=[],
      entry_points={
          'console_scripts': [
              'giftoa = giftoa.giftoa:main',
              'rightgif = giftoa.rightgif:main'
          ]
      },
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: BSD License',
          'Intended Audience :: End Users/Desktop',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Artistic Software',
          'Topic :: Utilities',
      ]
)
