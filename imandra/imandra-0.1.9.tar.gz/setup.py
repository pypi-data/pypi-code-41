import re
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup\
  ( name='imandra'
  , packages=[package for package in find_packages() if package.startswith('imandra')]
  , install_requires=[ "requests" ]  
  , description='Imandra python: formal verification and reasoning about python programs'
  , long_description=long_description
  , long_description_content_type="text/markdown"
  , author='Imandra'
  , url='http://imandra.ai'
  , author_email='kostya@aestheticintegration.com'
  , version='0.1.9'
  , classifiers=\
    [ "Programming Language :: Python :: 3"
    , "Operating System :: OS Independent"
    ]

  )
