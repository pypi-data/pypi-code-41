# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

setup(
    name='transporthours',
    version='0.0.1',
    description='Package for handling public transport routes opening hours from OpenStreetMap',
    long_description_content_type='text/markdown',
    long_description=readme,
    author='Adrien Pavie & Jungle Bus',
    author_email='panieravide@riseup.net',
    url='https://github.com/JungleBus/transport-hours-py',
    license='GNU LGPLv3',
    packages=find_packages(exclude=('tests')),
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Software Development :: Libraries"
    ],
    python_requires='>=2.7'
)
