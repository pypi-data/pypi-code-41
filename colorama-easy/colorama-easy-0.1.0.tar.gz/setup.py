# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['coloramaeasy']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.1,<0.5.0']

setup_kwargs = {
    'name': 'colorama-easy',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'xmonader',
    'author_email': 'xmonader@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
