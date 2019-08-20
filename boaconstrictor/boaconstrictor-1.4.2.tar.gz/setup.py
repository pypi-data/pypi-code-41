import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()
#1.2.11
# This call to setup() does all the work
setup(
	name="boaconstrictor",
	version='1.4.2',
	description='Compiler for the BoaConstrictor programming language.',
	long_description=README,
	long_description_content_type="text/markdown",
	url='https://github.com/thescribe11/BoaConstrictor',
	author='Adam Raschio',
	author_email='thescribe11@gmail.com',
	license='MIT',
	classifiers=[
		"License :: OSI Approved :: MIT License",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.7",
		"Development Status :: 5 - Production/Stable",
		"Environment :: Console",
		"Topic :: Software Development :: Compilers",
	],
	packages=find_packages(),
	install_requires=["pyinstaller"],
	entry_points={
		"console_scripts": [
			'boaconstrictor=BoaConstrictor.BoaConstrictor:main',
			'BoaConstrictor=BoaConstrictor.BoaConstrictor:main',
			'bc=BoaConstrictor.BoaConstrictor:main',]},
	setup_requires=['wheel']
	)
