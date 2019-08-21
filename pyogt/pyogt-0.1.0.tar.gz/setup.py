"""Setup script for pyogt."""
from setuptools import setup, find_packages

setup(
    name='pyogt',
    version='0.1.0',
    author='Claes Hallstrom',
    author_email='hallstrom.claes@gmail.com',
    description='Retrieve departure information from OstgotaTrafiken',
    license='Apache License 2.0',
    url='https://github.com/claha/pyogt',
    packages=find_packages(exclude=['tests', 'tests.*']),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
    ],
)
