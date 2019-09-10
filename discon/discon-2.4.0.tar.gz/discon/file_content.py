_SETUP_PY = """# Fallowing command is used to upload to pipy
#    python setup.py register sdist upload
from setuptools import setup, find_packages
# Always prefer setuptools over distutils
from os import path

here = path.abspath(path.dirname(__file__))
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='{name}',
    description='{description}',
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version='0.0.0',
    url='https://github.com/{githublogin}/{name}',
    author='{author}',
    author_email='{email}',
    license='{license}',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Bio-Informatics',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: BSD License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # 'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.2',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords='{keywords}',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=["examples", "devel", 'dist',  'docs', 'tests*']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/technical.html#install-requires-vs-requirements-files
    install_requires=[
    # 'numpy', 'conda'
    ],
    # 'SimpleITK'],  # Removed becaouse of errors when pip is installing
    dependency_links=[],

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # package_data={{
    #     'sample': ['package_data.dat'],
    #     If any package contains *.txt or *.rst files, include them:
    #     '': ['*.txt', '*.xml', '*.special', '*.huh'],
    # }},
    # package_data={
    #     "sample1": ["anwa.png"],
    #     "": ["*.png", "*.ico"],
    #     "sample2": ["anwa/anwa.png"],
    # },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages.
    # see
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # entry_points={{
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # }},
)
"""

_SETUP_CFG = """
[bumpversion]
current_version = 0.0.0
files = setup.py conda-recipe/meta.yaml
commit = True
tag = True
tag_name = {new_version}

# [nosetests]
# attr = !interactive,!slow

[tool:pytest]
addopts = -m "not interactive and not slow"
markers =
    interactive: marks interactive tests
    slow: marks slow tests
"""

_META_YML = """package:
  name: {name}
  version: "0.0.0"

source:
# this is used for build from git hub
  git_rev: 0.0.0
  git_url: https://github.com/{githublogin}/{name}.git

# this is used for pypi
  # fn: io3d-1.0.30.tar.gz
  # url: https://pypi.python.org/packages/source/i/io3d/io3d-1.0.30.tar.gz
  # md5: a3ce512c4c97ac2410e6dcc96a801bd8
#  patches:
   # List any patch files here
   # - fix.patch

build:
  noarch: python
  ignore_prefix_files:
    - devel
    - examples
  
  # noarch_python: True
  # preserve_egg_dir: True
  # entry_points:
    # Put any entry points (scripts to be generated automatically) here. The
    # syntax is module:function.  For example
    #
    # - {name} = {name}:main
    #
    # Would create an entry point called io3d that calls {name}.main()


  # If this is a new build for the same version, increment the build
  # number. If you do not include this key, it defaults to 0.
  # number: 1

requirements:
  build:
    - python
    - setuptools
    # - {{ pin_compatible('imma', max_pin='x.x') }}

  run:
    - python
    # - {{ pin_compatible('imma', max_pin='x.x') }}
    # - numpy
    # - pyqt 4.11.* # [not win]
    # - pyqt 4.12.2 # [win]

test:
  # Python imports
  imports:
    - {name}

  # commands:
    # You can put test commands to be run here.  Use this to test that the
    # entry points work.


  # You can also put a file called run_test.py in the recipe that will be run
  # at test time.

  # requires:
    # Put any additional test requirements here.  For example
    # - nose

about:
  home: https://github.com/{githublogin}/{name}
  license: {license}
  summary: {description}

# See
# http://docs.continuum.io/conda/build.html for
# more information about meta.yaml
"""


_CONDARC = """#!/bin/bash

$PYTHON setup.py install

# Add more build steps here, if they are necessary.

# See
# http://docs.continuum.io/conda/build.html
# for a list of environment variables that are set during the build process.
"""

_TRAVIS_YML="""language: python
python: 2.7
os: 
  - linux
  # - osx
  # - windows
# Ubuntu 14.04 Trusty support
sudo: required
# dist: trusty
# install new cmake
#addons:
#  apt:
#    packages:
#      - cmake
#    sources:
#      - kalakris-cmake
env:
    # - CONDA_PYTHON_VERSION=2.7
    - CONDA_PYTHON_VERSION=3.6
    - CONDA_PYTHON_VERSION=3.7

services:
  - xvfb
matrix:
  include:
    - os: osx
      language: minimal
      name: osx python36
      env:
        - CONDA_PYTHON_VERSION=3.6
    - os: osx
      language: minimal
      name: osx python37
      env:
        - CONDA_PYTHON_VERSION=3.7
  allow_failures:
    - env: CONDA_PYTHON_VERSION=2.7
    - env: CONDA_PYTHON_VERSION=3.7
    # - os: windows
  fast_finish: true
# virtualenv:
#   system_site_packages: true
before_script:
    # GUI
    - "export DISPLAY=:99.0"

before_install:
    - sudo apt-get update
    # - sudo apt-get install -qq cmake libinsighttoolkit3-dev libpng12-dev libgdcm2-dev
    
    # - wget http://home.zcu.cz/~mjirik/lisa/install/install_conda.sh && source install_conda.sh
    - wget https://raw.githubusercontent.com/mjirik/discon/master/tools/install_conda.sh && source install_conda.sh
    # We do this conditionally because it saves us some downloading if the
    # version is the same.
    # - if [[ "$CONDA_PYTHON_VERSION" == "2.7" ]]; then
    #     echo "python 2"
    #   else
    #     echo "python 3"
    #   fi
    - hash -r
    - conda config --set always_yes yes --set changeps1 no
    - conda config --add channels mjirik
    - conda config --add channels conda-forge
    # - conda config --add channels SimpleITK
    # - conda config --add channels luispedro
    - conda update -q conda
    # Useful for debugging any issues with conda
    - conda info -a

# command to install dependencies
install:

    # - sudo apt-get install -qq $(< apt_requirements.txt)
    - conda create --yes -n travis python=$CONDA_PYTHON_VERSION
    - source activate travis
#    - Install dependencies
    - conda install --yes --file requirements_conda.txt pytest-cov coveralls
#    - pip install -r requirements_pip.txt
#    - "echo $LD_LIBRARY_PATH"
#    - "pip install -r requirements.txt"
#    - 'mkdir build'
#    - "cd build"
#    - "cmake .."
#    - "cmake --build ."
#    - "sudo make install"
#    - pip install .
#    - "cd .."
#    - 'echo "include /usr/local/lib" | sudo tee -a /etc/ld.so.conf'
#    - 'sudo ldconfig -v'
#    - conda list -e
#    - python -m io3d.datasets -l 3Dircadb1.1 jatra_5mm exp_small sliver_training_001 io3d_sample_data head volumetrie
# command to run tests
# script: nosetests -v --with-coverage --cover-package={name}

script: python -m pytest --cov={name}/
after_success: coveralls
"""

_TESTS_MAIN_PY = """\
#! /usr/bin/python
# -*- coding: utf-8 -*-

# import logging
# logger = logging.getLogger(__name__)
from loguru import logger
import pytest
import os.path

path_to_script = os.path.dirname(os.path.abspath(__file__))

def inc(x):
    return x + 1



# @pytest.mark.interactive
# @pytest.mark.slow
def test_answer():
    assert inc(3) == 5
"""

README_MD = """\
  
[![Build Status](https://travis-ci.org/{githublogin}/{name}.svg?branch=master)](https://travis-ci.org/{githublogin}/{name})
[![Coverage Status](https://coveralls.io/repos/github/{githublogin}/{name}/badge.svg?branch=master)](https://coveralls.io/github/{githublogin}/{name}?branch=master)
[![PyPI version](https://badge.fury.io/py/{name}.svg)](http://badge.fury.io/py/{name})


{name}

{description}

"""
