try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os

setup(
    name='bluenaas_capabilities',
    version='0.0.1',
    author='Shailesh Appukuttan',
    author_email='shailesh.appukuttan@unic.cnrs-gif.fr',
    url='https://github.com/appukuttan-shailesh/bluenaas_capabilities/',
    keywords = ['BlueNaaS', 'SciUnit', 'NEURON', 'python', 'validation framework'],
    license='MIT',
    description='A SciUnit library for handling NEURON-Python models having different internal implementations/formats.',
    long_description="",
    install_requires=['sciunit>=0.2.1.1', 'neuron'],
    py_modules=["bluenaas_capabilities"]
)
