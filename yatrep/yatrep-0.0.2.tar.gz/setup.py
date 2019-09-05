from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

setup(
    name='yatrep',
    version='0.0.2',
    description='Unity tests results xml parser tool',
    long_description='Unity tests results xml parser tool',
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=[]),
    python_requires='>=3.4',
    install_requires=[],
    extras_require={
        'dev': [],
        'test': [],
    },
    entry_points={}
)
