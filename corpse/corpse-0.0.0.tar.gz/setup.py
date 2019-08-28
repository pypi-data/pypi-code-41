import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="corpse",
    version="0.0.0",
    author="Romke van Dijk",
    author_email="mail+pypi@ocbios.nl",
    description="Package reservation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zyronix/corpse",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3.6",
        "Operating System :: POSIX :: Linux",
    ],
)
