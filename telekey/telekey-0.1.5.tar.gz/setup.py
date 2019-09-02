import os.path
from setuptools import setup

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))
print(HERE)

with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

with open(os.path.join(HERE, "requirements.txt")) as fid:
    REQUIREMENTS = fid.read().split()

# This call to setup() does all the work
setup(
    name="telekey",
    version="0.1.5",
    description="An Easy way to develop telegram bots",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/danialkeimasi/telekey",
    author="Danial Keimasi",
    author_email="danialkeimasi@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages=["telekey"],
    include_package_data=True,
    install_requires=REQUIREMENTS,
    entry_points={"console_scripts": ["telekey=telekey.__main__:main"]},
)
