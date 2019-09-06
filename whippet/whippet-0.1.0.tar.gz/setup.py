# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['whippet']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['whippet = whippet:console.run']}

setup_kwargs = {
    'name': 'whippet',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Dalibor Novak',
    'author_email': 'BorePlusPlus@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
