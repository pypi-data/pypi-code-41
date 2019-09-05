# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['shreqt']

package_data = \
{'': ['*']}

install_requires = \
['pyexasol>=0.6.4,<0.7.0',
 'sqlalchemy-exasol>=2.0,<3.0',
 'sqlalchemy>=1.3,<2.0',
 'sqlparse>=0.3.0,<0.4.0']

setup_kwargs = {
    'name': 'shreqt',
    'version': '0.2.3',
    'description': '',
    'long_description': None,
    'author': 'Zibi Rzepka',
    'author_email': 'zibi.rzepka@revolut.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
