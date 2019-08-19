# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['tyme']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'tyme',
    'version': '0.1.0',
    'description': 'track your moments everywhere',
    'long_description': None,
    'author': 'Enrico Borba',
    'author_email': 'enricozb@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
