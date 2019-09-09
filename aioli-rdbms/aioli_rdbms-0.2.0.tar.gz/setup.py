# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['aioli_rdbms']

package_data = \
{'': ['*']}

install_requires = \
['aioli>=0.5.0,<0.6.0',
 'aiomysql>=0.0.20,<0.0.21',
 'asyncpg>=0.18.3,<0.19.0',
 'databases>=0.2.1,<0.3.0',
 'mysqlclient>=1.4.2,<2.0.0',
 'orm>=0.1,<0.2',
 'psycopg2-binary>=2.8.1,<3.0.0']

setup_kwargs = {
    'name': 'aioli-rdbms',
    'version': '0.2.0',
    'description': 'ORM and CRUD Service for Aioli with support for MySQL and PostgreSQL',
    'long_description': '',
    'author': 'Robert Wikman',
    'author_email': 'rbw@vault13.org',
    'url': 'https://github.com/aioli-framework/aioli-rdbms',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
