# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['the_pet']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=0.25.1,<0.26.0']

setup_kwargs = {
    'name': 'the-pet',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'James Maxwell',
    'author_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
