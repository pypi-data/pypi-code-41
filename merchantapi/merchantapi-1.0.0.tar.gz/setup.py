"""
 * This file is part of the MerchantAPI package.
 *
 * (c) Miva Inc <https://www.miva.com/>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 *
 * $Id: setup.py 77503 2019-08-21 21:22:55Z gidriss $
"""

import sys
from setuptools import setup, find_packages
from merchantapi.version import Version

setup(
    name='merchantapi',
    version=Version.STRING,
    license=open('LICENSE').read().strip(),
    author='Miva Inc',
    url='https://www.miva.com',
    description='Miva Merchant JSON API SDK',
    packages=find_packages(exclude=['examples', 'tests']),
    py_modules=['merchantapi'],
    install_requires=['requests'],
    zip_safe=False,
    keywords='miva merchant json api sdk',
)
