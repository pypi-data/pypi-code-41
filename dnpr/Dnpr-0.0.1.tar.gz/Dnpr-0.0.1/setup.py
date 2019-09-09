import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Dnpr",
    version="0.0.1",
    author="Satyaki De",
    author_email="satyaki.de@gmail.com",
    description="Useful Data manipulation functions for JSON.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SatyakiDe2019/Dnpr",
    packages=setuptools.find_packages(),
	install_requires=[
          'markdown','pandas','regex',
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)