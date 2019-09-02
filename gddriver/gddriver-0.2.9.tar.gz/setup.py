# -*- coding: utf-8 -*-

__author__ = 'Rao Mengnan'

import os

try:
    import setuptools
except ImportError:
    import distutils.core as setuptools


location = os.path.dirname(os.path.abspath(__file__))
about = {}
with open(os.path.join(location, 'gddriver/__about__.py'), 'r') as f:
    exec(f.read(), about)

requirements = [
    'crcmod',
    'oss2>=2.4.0'
]

test_requirements = ['mock']

packages = setuptools.find_packages(exclude=['tests', 'tests.*'])
setuptools.setup(
    name='gddriver',
    description="The gddriver is an efficient tool for operating the storage service such as oss and ftp.",
    version=about['VERSION'],
    author='GeneDock Contributor',
    author_email="raomengnan@genedock.com",
    maintainer='GeneDock Contributor',
    maintainer_email='raomengnan@genedock.com',
    url='https://genedock.com',
    packages=packages,
    package_data={'': ['LICENSE', 'requirements.txt']},
    license='ASF',

    platforms=['Independent'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    tests_require=test_requirements,
    test_suite='tests'
)
