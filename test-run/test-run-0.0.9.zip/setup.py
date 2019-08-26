from setuptools import setup
def readme():
	with open('README.md') as f:
		README=f.read()
	return README

setup(
	name="test-run",
	version="0.0.9",
	description="A Python package to print",
	long_description=readme(),
	long_description_content_type=["text/markdown"],
	author="ANOOP SINGH RANA",
	author_email="apours986@gmail.com",
	license="MIT",
	classifiers=[
		"Programming Language :: Python :: 2",
	],
	#packages="test_run", thisw was for python3 but u need each nd every directory separately
	packages=["test_run"],
	include_package_data=True,
	install_requires=["numpy"],
	entry_points={
		"console_scripts":  [
			"test-run=test_run.test1:main",
		]
	},
)
