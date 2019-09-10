# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['novlake']

package_data = \
{'': ['*']}

install_requires = \
['awswrangler>=0.0.1,<0.0.2',
 'boto3>=1.9,<2.0',
 'python-dotenv>=0.10.3,<0.11.0']

setup_kwargs = {
    'name': 'novlake',
    'version': '0.1.0',
    'description': 'Tools to work with our data lake',
    'long_description': None,
    'author': 'Pierre-Marie Leveque',
    'author_email': 'pierre@noverde.com.br',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
