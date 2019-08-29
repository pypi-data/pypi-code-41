"""
setuptools for project

python setup.py bdist_wheel

"""

from setuptools import setup

with open("requirements.txt") as f:
    requires = [l for l in f.read().splitlines() if l]

setup(
    name='easysubpub',
    version='0.0.1',
    packages=['easysubpub'],
    include_package_data=True,
    install_requires=requires,
    platforms='any',
)
