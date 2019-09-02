import os
import formatter as metadata
from setuptools import setup, find_packages

long_description = open('README.md').read()

setup(
    name=metadata.__package_name__,
    version=metadata.__version__,
    author=metadata.__author__,
    author_email=metadata.__author_email__,
    description=metadata.__description__,
    url=metadata.__url__,
    license='BSD',
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type='text/markdown',
    test_suite='nose.collector',
    install_requires=[
        'marshmallow', 'requests'
    ],
    py_modules=['formatter'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
    ],
    entry_points={
        'console_scripts': [
            'formatter = formatter.main:main',
        ],
    },
)