#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='csvgather'
      ,url='https://bitbucket.org/adamlabadorf/csvgather/overview'
      ,version=open('VERSION').read().strip()
      ,description=('A tool for collecting sets of character separated value '
        'files and joining into a single matrix file with column selection and '
        'column name manipulation operations'
       )
      ,author='Adam Labadorf'
      ,author_email='alabadorf@gmail.com'
      ,license='MIT'
      ,python_requires='>= 3'
      ,packages=find_packages()
      ,install_requires=[
          'docopt',
          'pandas>=0.21.0'
      ]
      ,entry_points={
        'console_scripts': [
          'csvgather=csvgather:main'
        ]
      }
      ,setup_requires=['pytest-runner']
      ,tests_require=['pytest']
      ,classifiers=[
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 5 - Production/Stable',

          # Indicate who your project is intended for
          'Intended Audience :: Science/Research',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'Topic :: Utilities',

          # Pick your license as you wish (should match "license" above)
          'License :: OSI Approved :: MIT License',

          # Specify the Python versions you support here. In particular, ensure
          # that you indicate whether you support Python 2, Python 3 or both.
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',

          'Environment :: Console'
      ]
     )
