import setuptools
from setuptools.command.install import install

with open("README.md", "r") as fh:
    long_description = fh.read()
with open("requirements.txt") as fr:
    install_requires = fr.read().splitlines()

setuptools.setup(
    name="impress-padmec",
    version="1.0.1",
    author="Artur Castiel, Gabriel Mendes",
    description="Intuitive Multilevel Preprocessor for Smart Simulation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires = install_requires,
    url="https://github.com/padmec-reservoir/impress",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
)
