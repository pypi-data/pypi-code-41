from distutils.core import setup
import setuptools

setup(
    name = 'stspy',
    version='1.0.0',
    packages=setuptools.find_packages(exclude=['test']),
    license='GNU GENERAL PUBLIC LICENSE',
    description='Scanning Tunneling Spectra Analysis in Python',
    long_description=open('README.txt').read(),
)
