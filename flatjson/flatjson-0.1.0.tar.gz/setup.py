# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['flatjson']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'flatjson',
    'version': '0.1.0',
    'description': 'Flatten json.',
    'long_description': None,
    'author': 'Jiuli Gao',
    'author_email': 'gaojiuli@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
