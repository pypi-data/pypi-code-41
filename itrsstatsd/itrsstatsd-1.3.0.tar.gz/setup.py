# Copyright 2019 ITRS Group Ltd. All rights reserved.
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("CHANGELOG.md", "r") as fh:
    long_description += '\n\n' + fh.read()

setup(
    name='itrsstatsd',
    version='1.3.0',
    description='ITRS StatsD Client',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://www.itrsgroup.com',
    author='ITRS Group Ltd.',
    author_email='support@itrsgroup.com',
    license='BSD',
    packages=['itrsstatsd'],
    zip_safe=False,
    python_requires='>=3.7',
    classifiers=[
          "Operating System :: OS Independent",
          "Programming Language :: Python ",
          "Programming Language :: Python :: 3.7",
          "Topic :: System :: Monitoring",
          "Intended Audience :: Developers"
    ]
)
