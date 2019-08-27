from setuptools import setup, find_packages
from podder_lib import __version__ as podder_lib_version

with open('requirements.txt') as file:
    install_requires = file.read()

setup(
    name='podder-lib',
    version=podder_lib_version,
    description='Library for the Podder Task.',
    packages=find_packages(),
    author="podder-ai",
    url='https://github.com/podder-ai/podder-lib',
    include_package_data=True,
    install_requires=install_requires
)
