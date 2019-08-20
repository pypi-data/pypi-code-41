# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['ezlock']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'ezlock',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': '0Hughman0',
    'author_email': 'rammers2@hotmail.co.uk',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
