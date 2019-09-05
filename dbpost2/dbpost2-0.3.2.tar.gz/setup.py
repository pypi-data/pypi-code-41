# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
setup(
    name="dbpost2",
    version="0.3.2",
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    install_requires=['pymongo', 'dataset'],
    url="https://github.com/dantezhu/dbpost",
    license="BSD",
    author="grey",
    author_email="greyeee@gmail.com",
    description="proxy for save db data. support mysql、sqlite、mongodb",
)
