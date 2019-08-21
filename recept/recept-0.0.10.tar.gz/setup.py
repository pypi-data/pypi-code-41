import io
from setuptools import setup, find_packages
from recept.version import __version__

author = "Viktor Kerkez"
author_email = "alefnula@gmail.com"
url = "https://github.com/alefnula/recept"


setup(
    name="recept",
    version=__version__,
    author=author,
    author_email=author_email,
    maintainer=author,
    maintainer_email=author_email,
    url=url,
    description="Recipe runner and a recipes functions library.",
    long_description=io.open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    platforms=["Windows", "POSIX", "MacOS"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
    license="Apache-2.0",
    packages=find_packages(),
    install_requires=io.open("requirements.txt").read().splitlines(),
    entry_points="""
        [console_scripts]
        rr=recept.__main__:main
    """,
)
