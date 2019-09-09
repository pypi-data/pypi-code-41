# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['lib2']

package_data = \
{'': ['*']}

install_requires = \
['01d61084-d29e-11e9-96d1-7c5cf84ffe8e>=0.1.0,<0.2.0',
 'attrs==19.1.0',
 'click==7.0']

entry_points = \
{'console_scripts': ['lib2 = lib2.cli:cli']}

setup_kwargs = {
    'name': 'e5fda7ba-d2a1-11e9-96d1-7c5cf84ffe8e',
    'version': '0.1.0',
    'description': '',
    'long_description': '========\nOverview\n========\n\n.. start-badges\n\n.. list-table::\n    :stub-columns: 1\n\n    * - docs\n      - |docs|\n    * - tests\n      - | |travis| |appveyor|\n        |\n    * - package\n      - | |version| |wheel| |supported-versions| |supported-implementations|\n        | |commits-since|\n\n.. |docs| image:: https://readthedocs.org/projects/lib2/badge/?style=flat\n    :target: https://readthedocs.org/projects/lib2\n    :alt: Documentation Status\n\n\n.. |travis| image:: https://travis-ci.org/python-retool/lib2.svg?branch=master\n    :alt: Travis-CI Build Status\n    :target: https://travis-ci.org/python-retool/lib2\n\n.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/python-retool/lib2?branch=master&svg=true\n    :alt: AppVeyor Build Status\n    :target: https://ci.appveyor.com/project/python-retool/lib2\n\n.. |version| image:: https://img.shields.io/pypi/v/1274c9e8-d29f-11e9-96d1-7c5cf84ffe8e.svg\n    :alt: PyPI Package latest release\n    :target: https://pypi.org/pypi/1274c9e8-d29f-11e9-96d1-7c5cf84ffe8e\n\n.. |commits-since| image:: https://img.shields.io/github/commits-since/python-retool/lib2/v0.1.0.svg\n    :alt: Commits since latest release\n    :target: https://github.com/python-retool/lib2/compare/v0.1.0...master\n\n.. |wheel| image:: https://img.shields.io/pypi/wheel/1274c9e8-d29f-11e9-96d1-7c5cf84ffe8e.svg\n    :alt: PyPI Wheel\n    :target: https://pypi.org/pypi/1274c9e8-d29f-11e9-96d1-7c5cf84ffe8e\n\n.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/1274c9e8-d29f-11e9-96d1-7c5cf84ffe8e.svg\n    :alt: Supported versions\n    :target: https://pypi.org/pypi/1274c9e8-d29f-11e9-96d1-7c5cf84ffe8e\n\n.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/1274c9e8-d29f-11e9-96d1-7c5cf84ffe8e.svg\n    :alt: Supported implementations\n    :target: https://pypi.org/pypi/1274c9e8-d29f-11e9-96d1-7c5cf84ffe8e\n\n\n.. end-badges\n\nAn example package. Generated with cookiecutter-pylibrary.\n\n* Free software: BSD 2-Clause License\n\nInstallation\n============\n\n::\n\n    pip install 1274c9e8-d29f-11e9-96d1-7c5cf84ffe8e\n\nDocumentation\n=============\n\n\nhttps://lib2.readthedocs.io/\n\n\nDevelopment\n===========\n\nTo run the all tests run::\n\n    tox\n\nNote, to combine the coverage data from all the tox environments run:\n\n.. list-table::\n    :widths: 10 90\n    :stub-columns: 1\n\n    - - Windows\n      - ::\n\n            set PYTEST_ADDOPTS=--cov-append\n            tox\n\n    - - Other\n      - ::\n\n            PYTEST_ADDOPTS=--cov-append tox\n',
    'author': 'Full Name',
    'author_email': 'email@example.com',
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
