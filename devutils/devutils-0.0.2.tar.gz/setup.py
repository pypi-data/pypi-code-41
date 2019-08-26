import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="devutils",
    version="0.0.2",
    author="Naoto Usuyama",
    author_email="usuyama.naoto@gmail.com",
    description="various utils",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/usuyama/devutils",
    packages=setuptools.find_packages(exclude=('tests', 'docs')),
)
