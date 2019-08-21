import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="IndigoPy",
    version="0.0.1a1",
    author="Indigo Mad",
    author_email="indigomad@pku.edu.cn",
    description="Just A test now",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IndigoMad/IndigoPy.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
          'numpy','scipy','matplotlib'
      ],
)