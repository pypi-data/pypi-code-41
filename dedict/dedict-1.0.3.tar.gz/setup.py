from os import path

from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dedict',
    version='1.0.3',
    description='simple library to create objects from dictionaries',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Olivier Verville',
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    packages=['dedict']
)
