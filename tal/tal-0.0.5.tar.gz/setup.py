from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="tal",
    author="Ty Wood-Pavicich",
    author_email="devwoodpav@gmail.com",
    description="Build Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/woodpav/tal",
    version="0.0.5",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["click"],
    entry_points="""
        [console_scripts]
        tal=src:cli
    """,
)
