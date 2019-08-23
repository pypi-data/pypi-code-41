from setuptools import setup
import setuptools

setup(name='rfdist',
	version='0.9',
	author='Frank Hui',
	description="Python package implementing an improved version of the RF distribution computation by Bryant et al.",
	packages=setuptools.find_packages(),
      	install_requires=['numpy','ete3'],
	classifiers=[
	        "Programming Language :: Python :: 3",
	        "License :: OSI Approved :: MIT License",
	        "Operating System :: OS Independent",
	]
      )
