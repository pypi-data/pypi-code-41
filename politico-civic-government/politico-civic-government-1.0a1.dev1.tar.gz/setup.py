# Imports from python.
import os
from setuptools import find_packages
from setuptools import setup


# Imports from government.
from government import __version__


REPO_URL = "https://github.com/The-Politico/politico-civic-government/"

PYPI_VERSION = ".".join(str(v) for v in __version__)

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()


setup(
    name="politico-civic-government",
    version=PYPI_VERSION,
    packages=find_packages(exclude=["docs", "tests", "example"]),
    license="MIT",
    description=(
        "Manage government and party organizations, the POLITICO way."
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    url=REPO_URL,
    download_url="{repo_url}archive/{version}.tar.gz".format(
        **{"repo_url": REPO_URL, "version": PYPI_VERSION}
    ),
    author="POLITICO interactive news",
    author_email="interactives@politico.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Framework :: Django :: 2.0",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet :: WWW/HTTP",
    ],
    keywords="",
    install_requires=[
        "django",
        "djangorestframework",
        "dj-database-url",
        "psycopg2-binary",
        "politico-civic-utils",
        "politico-civic-entity",
        "politico-civic-geography",
        "tqdm",
        "us",
    ],
    extras_require={
        "dev": ["sphinx", "sphinxcontrib-django", "sphinx-rtd-theme"],
        "test": ["pytest"],
    },
)
