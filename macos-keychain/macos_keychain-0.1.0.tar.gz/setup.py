# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['macos_keychain']

package_data = \
{'': ['*']}

install_requires = \
['sh>=1.12,<2.0']

setup_kwargs = {
    'name': 'macos-keychain',
    'version': '0.1.0',
    'description': 'A Simple MacOS Keychain Store',
    'long_description': None,
    'author': 'Juan Gonzalez',
    'author_email': 'jrg2156@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
