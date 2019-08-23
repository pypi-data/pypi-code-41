# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['crapy']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'crapy',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'jessekrubin',
    'author_email': 'jessekrubin@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
