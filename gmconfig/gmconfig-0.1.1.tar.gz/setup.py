# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['gmconfig']

package_data = \
{'': ['*']}

install_requires = \
['pyyaml>=5.1,<6.0']

setup_kwargs = {
    'name': 'gmconfig',
    'version': '0.1.1',
    'description': 'My lazy mans config loading and exporting module',
    'long_description': None,
    'author': 'GeekMasher',
    'author_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
