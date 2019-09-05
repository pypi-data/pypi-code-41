    
from setuptools import setup,find_packages


packages=find_packages(where=".")

setup(
    name='tfloop',
    version='0.2',
    description='tensorflow utils',
    author='lmaxwell',
    packages=packages,
)