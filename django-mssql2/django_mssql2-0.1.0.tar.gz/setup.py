# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['django_mssql2', 'django_mssql2.pyodbc']

package_data = \
{'': ['*']}

install_requires = \
['Cython>=0.29.13,<0.30.0', 'django>=2.2,<3.0', 'pymssql>=2.1,<3.0']

setup_kwargs = {
    'name': 'django-mssql2',
    'version': '0.1.0',
    'description': 'Django database adapter for MS SQL Server',
    'long_description': None,
    'author': 'Тряпчев Данил Павлович',
    'author_email': 'tryapchev@tochka.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
