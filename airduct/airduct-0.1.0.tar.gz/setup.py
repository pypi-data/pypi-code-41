# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['airduct']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0',
 'crontab>=0.22.6,<0.23.0',
 'pyyaml>=5.1,<6.0',
 'sqlalchemy>=1.3,<2.0']

setup_kwargs = {
    'name': 'airduct',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Skyler Lewis',
    'author_email': 'skyler.lewis@canopytax.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
