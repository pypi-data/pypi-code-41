# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['examples']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'examples',
    'version': '0.0.1',
    'description': 'Tests and Documentation Done by Example.',
    'long_description': 'Examples\n===============\n',
    'author': 'Timothy Crosley',
    'author_email': 'timothy.crosley@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
