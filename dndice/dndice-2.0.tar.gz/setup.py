# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dndice', 'dndice.lib']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['roll = rolling:roller.main']}

setup_kwargs = {
    'name': 'dndice',
    'version': '2.0',
    'description': 'An engine to parse and evaluate D&D-inspired roll expressions',
    'long_description': None,
    'author': 'Nick Thurmes',
    'author_email': 'nthurmes@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
