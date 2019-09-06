from setuptools import find_packages, setup

from simiotics.version import VERSION

setup(
    name='simiotics',
    version=VERSION,
    packages=find_packages(),
    install_requires=[
        'grpcio',
        'protobuf',
    ],
    description='Simiotics Python SDK',
    author='Neeraj Kashyap',
    author_email='neeraj@simiotics.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 3',
    ]
)
