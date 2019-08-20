# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['codaio']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.1,<20.0', 'python-dateutil>=2.8,<3.0', 'requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'codaio',
    'version': '0.1.0',
    'description': 'Python wrapper for Coda.io API',
    'long_description': '# Python wrapper for Coda.io API\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n',
    'author': 'MB',
    'author_email': 'mb@blaster.ai',
    'url': 'https://github.com/Blasterai/codaio',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
