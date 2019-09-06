from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize

extensions = [Extension("acrolib.cost_functions", ["src/acrolib/cost_functions.pyx"])]

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="acrolib",
    version="0.0.4",
    author="Jeroen De Maeyer",
    author_email="jeroen.demaeyer@kuleuven.be",
    description="General utilities for my robotics research at ACRO.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JeroenDM/acrolib",
    packages=find_packages(where="src"),
    install_requires=requirements,
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    ext_modules=cythonize(extensions),
    python_requires=">=3.6",
)
