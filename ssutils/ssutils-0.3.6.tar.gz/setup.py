import setuptools
with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name='ssutils',
	version='0.3.6',
	author="S Satapathy",
	author_email="shubhakant.satapathy@gmail.com",
	description="collection of useful python functions",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/satapathy/pypi-ssutils",
	packages=setuptools.find_packages(),
	install_requires=[
		'simple_salesforce',
	],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
 )
