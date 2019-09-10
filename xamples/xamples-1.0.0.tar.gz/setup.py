# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['xamples']

package_data = \
{'': ['*']}

install_requires = \
['examples>=0.0.2,<0.0.3']

setup_kwargs = {
    'name': 'xamples',
    'version': '1.0.0',
    'description': 'Tests and Documentation Done by Example. An alias for the project `examples` with better SEO opportunities',
    'long_description': None,
    'author': 'Timothy Crosley',
    'author_email': 'timothy.crosley@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
