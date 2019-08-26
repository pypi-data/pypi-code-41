import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="msachin_ashoka",
    version="0.1",
    author="Sachin Ashoka",
    author_email="sachin.mallade@iiitb.net",
    description="A sample package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sachinashoka/packages.git",
    packages=["msachin_ashoka"],
	include_package_data=True,
	install_requires=["requests"],
	classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
