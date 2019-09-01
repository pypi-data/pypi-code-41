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
def readme():
	with open('README.md') as f:
		README=f.read()
	return README

setup(
	name="test-run",
	version="0.0.23",
	description="A Python package to print",
	long_description=readme(),
	long_description_content_type=["text/markdown"],
	author="ANOOP SINGH RANA",
	author_email="apours986@gmail.com",
	license="MIT",
	classifiers=[
		"Programming Language :: Python :: 3",
	],
	#packages="test_run", thisw was for python3 but u need each nd every directory separately
	#package_dir={'':'test_run'},
	packages=["test_run"],
	include_package_data=True,
	entry_points={
		"console_scripts":  [
			"test-run=test_run._main:main",
		]
	},
)
