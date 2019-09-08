#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2019 Jürgen Mülbert. All rights reserved.
#
# Licensed under the EUPL, Version 1.2 or – as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
#
# https://joinup.ec.europa.eu/page/eupl-text-11-12
#
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.
#
# Lizenziert unter der EUPL, Version 1.2 oder - sobald
#  diese von der Europäischen Kommission genehmigt wurden -
# Folgeversionen der EUPL ("Lizenz");
# Sie dürfen dieses Werk ausschließlich gemäß
# dieser Lizenz nutzen.
# Eine Kopie der Lizenz finden Sie hier:
#
# https://joinup.ec.europa.eu/page/eupl-text-11-12
#
# Sofern nicht durch anwendbare Rechtsvorschriften
# gefordert oder in schriftlicher Form vereinbart, wird
# die unter der Lizenz verbreitete Software "so wie sie
# ist", OHNE JEGLICHE GEWÄHRLEISTUNG ODER BEDINGUNGEN -
# ausdrücklich oder stillschweigend - verbreitet.
# Die sprachspezifischen Genehmigungen und Beschränkungen
# unter der Lizenz sind dem Lizenztext zu entnehmen.
#

"""The setup.py file for Python openorders."""
from datetime import datetime as dt
from setuptools import setup, find_packages
import pkg_resources
import sys
import os
import io

with io.open("README.rst", "rt", encoding="utf8") as f:
    readme = f.read()

__version__ = "0.1.0"
MIN_PY_VERSION = "3.6"
PROJECT_NAME = "JM OpenOrders"
PROJECT_DESCRIPTION = (
    "jmopenorders is a generator to generate infos for the affected persons"
)
PROJECT_PACKAGE_NAME = "jmopenorders"
PROJECT_LICENSE = "EUPL-1.2 "
PROJECT_AUTHOR = "Jürgen Mülbert"
PROJECT_COPYRIGHT = " 2018-{}, {}".format(dt.now().year, PROJECT_AUTHOR)
PROJECT_URL = "https://jmopenorders.github.io/"
PROJECT_EMAIL = "juergen.muelbert@gmail.com"

PROJECT_GITHUB_USERNAME = "jmuelbert"
PROJECT_GITHUB_REPOSITORY = "jmopenorders"

PYPI_URL = "https://pypi.python.org/pypi/{}".format(PROJECT_PACKAGE_NAME)
GITHUB_PATH = "{}/{}".format(PROJECT_GITHUB_USERNAME, PROJECT_GITHUB_REPOSITORY)
GITHUB_URL = "https://github.com/{}".format(GITHUB_PATH)

DOWNLOAD_URL = "{}/archive/{}.zip".format(GITHUB_URL, __version__)
PROJECT_URLS = {"Bug Reports": "{}/issues".format(GITHUB_URL)}

# 'setup.py publish' shortcut.
if sys.argv[-1] == "publish":
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    sys.exit()

PACKAGES = find_packages(exclude=["tests", "tests.*"])

REQUIREMENTS = ["pexpect", "openpyxl", "python-slugify"]

test_requirements = ["tox"]

extras_require = {}

setup(
    name=PROJECT_PACKAGE_NAME,
    version=__version__,
    description=PROJECT_DESCRIPTION,
    long_description=readme,
    url=PROJECT_URL,
    download_url=DOWNLOAD_URL,
    project_urls=PROJECT_URLS,
    author=PROJECT_AUTHOR,
    author_email=PROJECT_EMAIL,
    packages=PACKAGES,
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    python_requires=">={}".format(MIN_PY_VERSION),
    test_suite="tests",
    tests_require=test_requirements,
    entry_points={"console_scripts": ["jmopenorders = jmopenorders.__main__:main"]},
)
