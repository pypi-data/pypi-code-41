# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['py_sugo']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'py-sugo',
    'version': '0.1.0',
    'description': 'Dependencyless WSGI compliant micro framework implemented with python using only the standard library.',
    'long_description': None,
    'author': 'Francisco Javier Sucre González',
    'author_email': 'franciscojsucreg@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
