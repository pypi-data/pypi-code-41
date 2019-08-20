import io
import os
import sys
from setuptools import setup, find_packages

# Package meta-data.
NAME = "dehinter"
DESCRIPTION = "A tool for the removal of TrueType instruction sets (hints) in fonts"
LICENSE = "Apache License v2.0"
URL = "https://github.com/source-foundry/dehinter"
EMAIL = "chris@sourcefoundry.org"
AUTHOR = "Source Foundry Authors and Contributors"
REQUIRES_PYTHON = ">=3.5.0"

INSTALL_REQUIRES = ["fontTools==3.44.0",
                    ]
# Optional packages
EXTRAS_REQUIRES = {
    # for developer installs
    "dev": ["wheel", "setuptools", "twine", "coverage", "pytest", "tox", "flake8", "pytype"]
}

this_file_path = os.path.abspath(os.path.dirname(__file__))

# Version
main_namespace = {}
version_fp = os.path.join(this_file_path, "lib", "dehinter", "__init__.py")
try:
    with io.open(version_fp) as v:
        exec(v.read(), main_namespace)
except IOError as version_e:
    sys.stderr.write(
        "[ERROR] setup.py: Failed to read the version data for the version definition: {}".format(
            str(version_e)
        )
    )
    raise version_e

# Use repository Markdown README.md for PyPI long description
try:
    with io.open("README.md", encoding="utf-8") as f:
        readme = f.read()
except IOError as readme_e:
    sys.stderr.write(
        "[ERROR] setup.py: Failed to read the README.md file for the long description definition: {}".format(
            str(readme_e)
        )
    )
    raise readme_e

setup(
    name=NAME,
    version=main_namespace["__version__"],
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    license=LICENSE,
    platforms=["Any"],
    long_description=readme,
    long_description_content_type="text/markdown",
    package_dir={"": "lib"},
    packages=find_packages("lib"),
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRES,
    python_requires=REQUIRES_PYTHON,
    entry_points={"console_scripts": ["dehinter = dehinter.__main__:main"]},
    classifiers=[
        "Environment :: Console",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Text Processing :: Fonts",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
    ],
)
