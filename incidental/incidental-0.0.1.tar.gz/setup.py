# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['incidental']

package_data = \
{'': ['*']}

install_requires = \
['invoke>=1.3,<2.0']

setup_kwargs = {
    'name': 'incidental',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'cloudcraeft',
    'author_email': 'cloudcraeft@outlook.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
