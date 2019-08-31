from setuptools import setup, find_packages
def readme():
	with open('README.md') as f:
		README=f.read()
	return README

setup(
	name="FIRSTRY",
	version="0.0.2",
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
	packages=["firstry"],
	include_package_data=True,
	entry_points={
		"console_scripts":  [
			"firstry=firstry._main:_main",
		]
	},
)
