import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = ["numpy", "pandas"]

devRequirements = [
    "pytest",
    "pytest-pep8",
    "pytest-cov",
    "setuptools",
    "wheel",
    "twine",
    "bumpversion"
]

setuptools.setup(
    name="quantfolio",
    version="0.3.1",
    author="Raymond Yeh",
    author_email="ray@geek.sg",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yehjxraymond/quantfolio",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    extras_require={"dev": devRequirements},
)
