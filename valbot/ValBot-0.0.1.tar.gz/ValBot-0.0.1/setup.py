import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ValBot",
    version="0.0.1",
    author="Deepali G",
    author_email="dgathibandhe@altair.com",
    description="Validation Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://gitlab.pclm.altair.com/pbsworks-validation/pbsworks-validation",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
