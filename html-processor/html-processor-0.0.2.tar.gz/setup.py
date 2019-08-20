# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['html_processor']

package_data = \
{'': ['*']}

install_requires = \
['bs4>=0.0.1,<0.0.2']

setup_kwargs = {
    'name': 'html-processor',
    'version': '0.0.2',
    'description': 'Package for creating HTML content processing templates',
    'long_description': '',
    'author': 'Дмитрий',
    'author_email': 'acrius@mail.ru',
    'url': 'https://github.com/brogency/html-processor',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
