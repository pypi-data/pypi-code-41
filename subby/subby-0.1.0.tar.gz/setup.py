# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['subby']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'subby',
    'version': '0.1.0',
    'description': 'Subprocesses simplified',
    'long_description': None,
    'author': 'jdidion',
    'author_email': 'github@didion.net',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
