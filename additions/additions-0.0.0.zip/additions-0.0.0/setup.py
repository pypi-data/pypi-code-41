
from setuptools import setup, find_packages


setup(
    name='additions',
    version='0.0.0',
    description="Additions to the Python Standard Library",
    packages=find_packages(exclude=['tests', 'tutorials']),
)