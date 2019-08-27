import setuptools
with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name='sheetcalc',
	version='0.1.6',
	author="S Satapathy",
	author_email="shubhakant.satapathy@gmail.com",
	description="extract insights from 2d tables",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/satapathy/pypi-sheetcalc",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
 )
