#!/usr/bin/env python

import os
import re
import setuptools

def read(fname):
  inf = open(os.path.join(os.path.dirname(__file__), fname))
  out = "\n" + inf.read().replace("\r\n", "\n")
  inf.close()
  return out

setuptools.setup(
  name='rca',

  version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('rca/rca.py').read(),
    re.M
    ).group(1),

  author='Kevin R Croft',
  author_email='krcroft@gmail.com',
  description='Recompress Audio',
  long_description=read('README.md') + '\n' + read('CHANGES.md'),
  long_description_content_type='text/markdown',
  url='https://gitlab.com/krcroft/rca',

  keywords='audio encoding vorbis ogg opus mp3 aac music speech mono stereo',

  packages=setuptools.find_packages(),
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: Implementation :: CPython',
    'Topic :: Multimedia :: Sound/Audio :: Conversion',
    'Topic :: Utilities'
  ],
  python_requires='>=3.5',

  install_requires=[
    'appdirs',
    'attrs',
    'colorlog',
    'yaml',
  ],

  entry_points={ 'console_scripts': ['rca = rca.rca:main'] },

  include_package_data=True,

  zip_safe=False)

