# # https://packaging.python.org/tutorials/packaging-projects/
# open $HOME/.pypirc
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="yellow-idea-py",
    version="0.2.9",
    author="Kittiphong Jittanupagorn",
    author_email="ragnarokmaster03@gmail.com",
    description="Yellow Idea SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="",
    packages=setuptools.find_packages()
)
