# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['mate3']

package_data = \
{'': ['*']}

install_requires = \
['pymodbus>=2.2,<3.0']

setup_kwargs = {
    'name': 'mate3',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Adam Charnock',
    'author_email': 'adam@adamcharnock.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
