# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['mate3']

package_data = \
{'': ['*']}

install_requires = \
['pymodbus>=2.2,<3.0']

entry_points = \
{'console_scripts': ['mate3 = mate3.main:main']}

setup_kwargs = {
    'name': 'mate3',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'Adam Charnock',
    'author_email': 'adam@adamcharnock.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
