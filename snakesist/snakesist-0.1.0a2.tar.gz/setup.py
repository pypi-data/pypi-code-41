# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['snakesist']

package_data = \
{'': ['*']}

install_requires = \
['delb>=0.1.0,<0.2.0', 'lxml>=4.3,<5.0', 'requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'snakesist',
    'version': '0.1.0a2',
    'description': 'A Python database connector for eXist-db',
    'long_description': None,
    'author': 'Theodor Costea',
    'author_email': 'theo.costea@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
