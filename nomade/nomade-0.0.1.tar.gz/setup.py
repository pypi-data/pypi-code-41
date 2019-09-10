# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['nomade']

package_data = \
{'': ['*'], 'nomade': ['assets/*', 'constants/*']}

install_requires = \
['click>=7.0,<8.0', 'pyyaml>=5.1,<6.0', 'sqlalchemy>=1.3,<2.0']

entry_points = \
{'console_scripts': ['nomade = nomade.main:cli']}

setup_kwargs = {
    'name': 'nomade',
    'version': '0.0.1',
    'description': 'Migration Manager for Humans',
    'long_description': '<p align="center">\n  <img src="https://github.com/kelvins/nomade/blob/master/artwork/logo.svg" alt="Nomade Logo" title="Nomade Logo" width="250" height="150" />\n</p>\n\n![Release Alpha](https://img.shields.io/badge/Release-alpha-orange.svg?style=flat-square)\n[![Python Version 3.7](https://img.shields.io/badge/Python-3.7-green.svg?style=flat-square)](https://www.python.org/downloads/release/python-370/)\n[![Code Style: black](https://img.shields.io/badge/Code%20Style-black-000000.svg?style=flat-square)](https://github.com/psf/black)\n[![License Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=flat-square)](https://github.com/kelvins/nomade/blob/master/LICENSE)\n\n> Python Migration Manager for Humans :camel:\n\nNomade is a simple migration manager tool that aims to be easy to integrate with any ORM.\n\n## Installation\n\nUse [pip](https://pip.pypa.io/en/stable/installing/) to install Nomade:\n\n```bash\n$ pip install nomade\n```\n\n## Quick Start\n\nInitialize a Nomade project:\n\n```bash\n$ nomade init\n```\n\nIt will create the following project structure:\n\n```\n.\n├── nomade\n│   ├── template.py\n│   └── migrations\n└── .nomade.yml\n```\n\nDefine **Nomade** settings in the `.nomade.yml` file.\n\nThen, create your first migration:\n\n```bash\n$ nomade migrate "My first migration"\n```\n\nImplement the `upgrade` and `downgrade` functions in the migration file.\n\nThen apply the migration to the database:\n\n```bash\n$ nomade upgrade head\n```\n\nTo discover more **Nomade** features please read the documentation or run:\n\n```bash\n$ nomade --help\n```\n\n## How to Contribute\n\n- Check for open issues or open a fresh one to start a discussion around a feature idea or a bug.\n- Become more familiar with the project by reading the [Contributor\'s Guide](CONTRIBUTING.rst).\n',
    'author': 'Kelvin S. do Prado',
    'author_email': 'kelvinpfw@gmail.com',
    'url': 'https://github.com/kelvins/nomade',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
