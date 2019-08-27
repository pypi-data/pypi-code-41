# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['tyme', 'tyme.cli']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.1,<0.5.0', 'hjson>=3.0,<4.0']

entry_points = \
{'console_scripts': ['tyme = tyme.cli.cli:main']}

setup_kwargs = {
    'name': 'tyme',
    'version': '0.1.5',
    'description': 'track your moments everywhere',
    'long_description': None,
    'author': 'Enrico Borba',
    'author_email': 'enricozb@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
