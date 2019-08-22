import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name = "docpy",
	version = "0.1.1",
	author = "Chris Pyles",
	author_email = "cpyles@berkeley.edu",
	description = "Python to MD documentation generator",
	long_description = long_description,
	long_description_content_type = "text/markdown",
	url = "https://github.com/chrispyles/docpy",
	license = "BSD-3-Clause",
	packages = setuptools.find_packages(),
	classifiers = [
		"Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
	],
	scripts=["bin/docpy"]
)