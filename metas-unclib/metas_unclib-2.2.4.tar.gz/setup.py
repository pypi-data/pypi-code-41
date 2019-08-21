import setuptools


with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="metas_unclib",
	version="2.2.4",
	author="Michael Wollensack",
	author_email="michael.wollensack@metas.ch",
	description="An advanced measurement uncertainty calculator",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://www.metas.ch/unclib",
	packages=setuptools.find_packages(),
	classifiers=[
		"License :: Other/Proprietary License",
		"Programming Language :: Python :: 2",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.4",
		"Programming Language :: Python :: 3.5",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
	],
	#install_requires=[
	#	'numpy',
	#	'scipy',
	#	'matplotlib',
	#	'pythonnet',
	#],
	include_package_data=True,
	zip_safe=False
)

