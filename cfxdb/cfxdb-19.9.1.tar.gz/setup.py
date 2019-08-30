##############################################################################
#
#                        Crossbar.io Fabric
#     Copyright (C) Crossbar.io Technologies GmbH. All rights reserved.
#
##############################################################################

import os
from setuptools import setup, find_packages


# read package version
with open('cfxdb/_version.py') as f:
    exec(f.read())  # defines __version__

# read package description
with open('README.rst') as f:
    docstr = f.read()


setup(
    name='cfxdb',
    version=__version__,  # noqa
    description='CrossbarFX edge ZLMDB database schema classes',
    long_description=docstr,
    author='Crossbar.io Technologies GmbH',
    author_email='support@crossbario.com',
    url='https://crossbario.com',
    license='proprietary',
    classifiers=['License :: Other/Proprietary License'],
    platforms=('Any'),
    install_requires=[
        'numpy==1.15.4',
        'zlmdb>=19.4.1',
    ],
    packages=find_packages(),
    zip_safe=True
)
