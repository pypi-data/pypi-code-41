from setuptools import setup, find_packages
from setuptools.extension import Extension

with open('README.md', 'r') as fh:
	long_description = fh.read()

alsmodule = Extension('als',
			sources = ['alsmodule.c'],
			extra_link_args = ['-framework', 'IOKit'])

setup(
	name='alsmodule-pkg',
	version='0.0.1',
	author='Jean-Jacques Puig',
	author_email='jjp-pypi@espci.fr',
	description='A simple module to access ambient light sensors samples on Mac OS X',
	long_description=long_description,
	long_description_content_type='text/markdown',
	packages=find_packages(),
	classifiers=[
		'Programming Language :: C',
		'Programming Language :: Python :: 3',
		'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
		'Operating System :: MacOS :: MacOS X',
	],
	python_requires='>=3.7',
        ext_modules = [alsmodule],
)
