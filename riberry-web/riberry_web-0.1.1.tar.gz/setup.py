# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['riberry_web']

package_data = \
{'': ['*'], 'riberry_web': ['webapp/*']}

install_requires = \
['fastapi[all]>=0.38.1,<0.39.0', 'riberry>=0.10.8,<0.11.0']

setup_kwargs = {
    'name': 'riberry-web',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
