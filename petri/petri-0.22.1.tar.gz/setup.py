# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['petri']

package_data = \
{'': ['*']}

install_requires = \
['autologging>=1.3,<2.0',
 'logzero>=1.5,<2.0',
 'pydantic>=0.30,<0.31',
 'python-dotenv>=0.10,<0.11',
 'toml>=0.10,<0.11',
 'tzlocal>=1.5,<2.0']

entry_points = \
{'console_scripts': ['petri = petri.__main__:_main']}

setup_kwargs = {
    'name': 'petri',
    'version': '0.22.1',
    'description': 'Handle project/application config from pyproject.toml',
    'long_description': '.. image:: https://travis-ci.org/pwoolvett/petri.svg?branch=master\n    :target: https://travis-ci.org/pwoolvett/petri\n    :alt: Build Status\n\n.. image:: https://readthedocs.org/projects/petri/badge/?version=latest\n   :target: https://petri.readthedocs.io/en/latest/?badge=latest\n   :alt: Documentation Status\n\n.. image:: https://api.codeclimate.com/v1/badges/f0f976249fae332a0bab/test_coverage\n   :target: https://codeclimate.com/github/pwoolvett/petri/test_coverage\n   :alt: Test Coverage\n\n\n.. image:: https://api.codeclimate.com/v1/badges/f0f976249fae332a0bab/maintainability\n   :target: https://codeclimate.com/github/pwoolvett/petri/maintainability\n   :alt: Maintainability\n\n.. image:: https://img.shields.io/badge/python%20version-3.6.7-275479.svg\n   :target: https://img.shields.io/badge/python%20version-3.6.7-275479.svg\n   :alt: Python Version\n\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://img.shields.io/badge/code%20style-black-000000.svg\n   :alt: Code Style\n\n\nSummary\n-------\nAvoid boilerplate python code.\n\nImporting petri automagically equips your script/pacakage with:\n\n* settings using pydantic.\n* dotenv file handling using python-dotenv.\n* logging config using logzero&autologging.\n* project metadata from a pyproject.toml file.\n* environment (prod/dev/test) handling via ENV environment variable.\n\nScreenshots\n-----------\n\n.. image:: static/screenshots/api.png\n\n\nCode Example\n------------\n\n* see tests/data folder\n\n\nRequirements\n------------\n\n- Usage requirements\n\n   + python>=3.6\n\n- Development requirements\n\n   + tox\n   + poetry (recommended)\n\n\nInstallation\n------------\n\n- pip install petri\n\nTesting\n-------\n\n- run `tox -e venv` to create an appropiate virtualenv\n- `tox` to run the full test suite\n\n\nContribute\n----------\n\n- Development\n   \n   + Make sure to pass tox tests (including those with `--runslow`).\n   + For tests design, you can use use ´@pytest.mark.incremental´ and  ´@pytest.mark.slow´. See "catalogo_db/tests/conftest.py"\n   + If the requirements change, make sure to re-build all images\n\n- Versioning\n   \n   + Use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/pwoolvett/petri/tags).\n\nSupport\n-------\n\nIf you are having issues, please file an issue in github.\n',
    'author': 'Pablo Woolvett',
    'author_email': 'pablowoolvett@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
