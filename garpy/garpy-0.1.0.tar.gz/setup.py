# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['garpy']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'garpy',
    'version': '0.1.0',
    'description': 'Python client for downloading activities from Garmin Connect',
    'long_description': None,
    'author': 'Felipe Aguirre Martinez',
    'author_email': 'felipeam86@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
