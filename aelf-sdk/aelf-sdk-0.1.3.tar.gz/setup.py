from setuptools import setup

setup(
    name='aelf-sdk',
    version='0.1.3',
    description='Python SDK for AElf',
    url='https://github.com/rosona/aelf-sdk.py',
    packages=['aelf'],
    install_requires=['requests', 'protobuf', 'base58', 'coincurve']
)
