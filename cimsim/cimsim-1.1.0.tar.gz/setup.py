# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cimsim']

package_data = \
{'': ['*']}

install_requires = \
['requests']

setup_kwargs = {
    'name': 'cimsim',
    'version': '1.1.0',
    'description': '',
    'long_description': None,
    'author': 'Airat',
    'author_email': 'airat_vi@mail.ru',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
