import setuptools


# with open("README.md", "r") as fh:
# 	long_description = fh.read()

long_description = "flask-mongoengine-orm makes your code more beautiful"


setuptools.setup(
	name = "flask-mongoengine-orm",
	version="0.0.6",
	auth="hxh",
	author_email="13750192465@163.com",
	description=long_description,
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/suckmybigdick/flask-mongoengine-orm",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	install_requires=[
		"flask==0.10.1",
		"mongoengine==0.18.0",
		"setuptools==41.0.1",
	],
)
