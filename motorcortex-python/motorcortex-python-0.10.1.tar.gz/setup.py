#!/usr/bin/python3

#
#   Developer : Alexey Zakharov (alexey.zakharov@vectioneer.com)
#   All rights reserved. Copyright (c) 2016 VECTIONEER.
#


from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='motorcortex-python',
      version='0.10.1',
      description='Python bindings for Motorcortex Engine',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Alexey Zakharov',
      author_email='alexey.zakharov@vectioneer.com',
      url='https://www.motorcortex.io',
      license='MIT',
      packages=['motorcortex', 'robot_control'],
      install_requires=['motorcortex-nanomsg', 
                        'protobuf', 
                        'futures; python_version == "2.7"', 
                        'future; python_version == "2.7"'],
      include_package_data=True, 
      )
