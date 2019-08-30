# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['centrifuge_cli']

package_data = \
{'': ['*']}

install_requires = \
['Click>=7.0,<8.0', 'pandas>=0.25.1,<0.26.0', 'requests>=2.22,<3.0']

entry_points = \
{'console_scripts': ['centrifuge = main:cli']}

setup_kwargs = {
    'name': 'centrifuge-cli',
    'version': '0.1.0',
    'description': "A command line utility for interacting with the Centrifuge Firmware Analysis Platform's REST API.",
    'long_description': '',
    'author': 'Peter Eacmen',
    'author_email': 'peacmen@refirmlabs.com',
    'url': 'https://www.refirmlabs.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
