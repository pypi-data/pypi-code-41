import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="pynumbpkg",
    version="1.3.0",
    description="get it all over here",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gist.githubusercontent.com/Rahul-Datta/8dde0ca1aeb9052c4d03c834c2e3bb52/raw/828535e4fcb834f80d7bb87ba6d5182161e2f71d/pypackages",
    author="Blobby",
    author_email="noemailsosorry@sorrymails.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["pynumbpkg"],
    include_package_data=True,
    install_requires=["feedparser", "html2text"],
    entry_points={
        "console_scripts": [
            "realpython=reader.__main__:main",
            ]
    },
)