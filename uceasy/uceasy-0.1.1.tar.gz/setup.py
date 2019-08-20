# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['uceasy', 'uceasy.adapters', 'uceasy.controller', 'uceasy.use_cases']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0', 'flask>=1.1,<2.0', 'pandas>=0.25.0,<0.26.0']

entry_points = \
{'console_scripts': ['uceasy = cli.uceasy_cli:uceasy']}

setup_kwargs = {
    'name': 'uceasy',
    'version': '0.1.1',
    'description': 'Wrapper for the Phyluce phylogenomics software package',
    'long_description': None,
    'author': 'Caio Raposo',
    'author_email': 'caioraposo@protonmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
