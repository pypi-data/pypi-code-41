from setuptools import setup, find_packages
from qoalai import version

setup(
    name='qoalai',  
    version=version,  
    description='a collection of coala ai library',  
    long_description="a collection of coala ai library",  
    author='qoala ai team',  
    packages=["qoalai", "qoalai.green_assesment", "qoalai.networks", "qoalai.segmentations"], 
)
