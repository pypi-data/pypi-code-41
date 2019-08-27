#!/usr/bin/env python

import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


def read_readme():
    with open('README.md') as f:
        return f.read()


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(name='polyaxon-pip-tests',
      version='0.0.5',
      description='Polyaxon package to group all std tests pip packages used in several projects',
      long_description=read_readme(),
      maintainer='Mourad Mourafiq',
      maintainer_email='mourad@polyaxon.com',
      author='Mourad Mourafiq',
      author_email='mourad@polyaxon.com',
      url='https://github.com/polyaxon/polyaxon-pip-tests',
      license='MIT',
      platforms='any',
      packages=find_packages(),
      keywords=[
          'polyaxon',
          'deep-learning',
          'machine-learning',
          'data-science',
          'neural-networks',
          'artificial-intelligence',
          'ai',
          'reinforcement-learning',
          'kubernetes',
      ],
      install_requires=[
          'coverage==4.5.1',
          'flake8==3.5.0',
          'flaky==3.4.0',
          'isort==4.3.4',
          'mock==2.0.0',
          'pep8-naming==0.7.0',
          'prospector==0.12.11',
          'pyflakes==1.6.0',
          'pytest==3.7.0',
          'pylint==1.8.4',
          'tox==3.1.2',
      ],
      extra={
          'black': ['black==19.3b0'],
      },
      classifiers=[
          'Programming Language :: Python',
          'Operating System :: OS Independent',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering :: Artificial Intelligence'
      ],
      tests_require=[
          "pytest",
      ],
      cmdclass={'test': PyTest})
