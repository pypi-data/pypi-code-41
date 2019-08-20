# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['barch']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0', 'xxhash>=1.3,<2.0']

setup_kwargs = {
    'name': 'barch',
    'version': '0.1.0',
    'description': 'Tool to support backup and archival',
    'long_description': None,
    'author': 'Joachim Hereth',
    'author_email': 'qudade-barch@quda.de',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
