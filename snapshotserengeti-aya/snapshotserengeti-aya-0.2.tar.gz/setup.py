import setuptools
with open("README.md","r") as fh:
	long_description = fh.read()

setuptools.setup(
	name='snapshotserengeti-aya',
	version='0.2',
	author='Aya Salama',
	author_email="aya_salama@aucegypt.edu",
	description="Snapshot Serengeti Dataset",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/Aya-S/Snapshot_Serengeti",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		],
)

