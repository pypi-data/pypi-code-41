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
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'Дмитрий',
    'author_email': 'acrius@mail.ru',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
