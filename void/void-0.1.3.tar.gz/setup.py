import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

setup(
    name='void',
    version='0.1.3',
    packages=['void'],
    description='Void object in Python',
    long_description=README,
    long_description_content_type='text/markdown',
    author='drozdowsky',
    author_email='hdrozdow+github@pm.me',
    url='https://github.com/drozdowsky/void/',
    license='MIT',
    install_requires=[
        'six'
    ],
)
