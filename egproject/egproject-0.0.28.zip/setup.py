from setuptools import setup, find_packages
import os
import sys
def find_packages(where='.'):
        # os.walk -> list[(dirname, list[subdirs], list[files])]
        return [folder.replace("/", ".").lstrip(".")
                for (folder, _, fils) in os.walk(where)
                if "__init__.py" in fils]

from io import open as io_open
src_dir = os.path.abspath(os.path.dirname(__file__))


install_requires = [ 'xlsxwriter', 'numpy','openpyxl','PIL']



def readme():
	with open('README.md') as f:
		README=f.read()
	return README

README_rst = ''
fndoc = os.path.join(src_dir, 'README.rst')
with io_open(fndoc, mode='r', encoding='utf-8') as fd:
    README_rst = fd.read()

setup(
	name="egproject",
	version="0.0.28",
	description="A Python package to print",
	long_description=README_rst,
	#long_description=open('README.md').read(),
	long_description_content_type=["text/markdown"],
	author="ANOOP SINGH RANA",
	author_email="apours986@gmail.com",
	license="MIT",
	classifiers=[
		"Programming Language :: Python :: 2.7",
	],
	#packages="test_run", thisw was for python3 but u need each nd every directory separately
	#package_dir={'':'test_run'},
	packages=["egproject"],
	install_requires=install_requires,
	include_package_data=True,
	entry_points={
		"console_scripts":  [
			"egproject=egproject._main:main",
		]
	},
)
