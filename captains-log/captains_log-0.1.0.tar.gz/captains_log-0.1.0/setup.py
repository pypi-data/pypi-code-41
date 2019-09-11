# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['captains_log']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'captains-log',
    'version': '0.1.0',
    'description': 'Out of this world log system',
    'long_description': None,
    'author': 'Juan Gonzalez',
    'author_email': 'jrg2156@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
