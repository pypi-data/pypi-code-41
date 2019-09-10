# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['switter']

package_data = \
{'': ['*']}

install_requires = \
['requests-html>=0.10.0,<0.11.0']

setup_kwargs = {
    'name': 'switter',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'michaeldel',
    'author_email': 'michaeldel@protonmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
