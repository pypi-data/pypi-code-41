from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="hostspy",
    version="0.1",
    author="Shahbaz Khan",
    author_email="shahbazkhan8194@gmail.com",
    description="Wraper around 'ss' linux command",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shahbazk8194/hostspy",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
)

