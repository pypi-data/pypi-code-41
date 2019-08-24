# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['fundoshi', 'fundoshi.sites', 'fundoshi.tests']

package_data = \
{'': ['*'], 'fundoshi.tests': ['cassettes/*']}

install_requires = \
['attrs>=19.1,<20.0',
 'beautifulsoup4>=4.8,<5.0',
 'lxml>=4.4,<5.0',
 'requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'fundoshi',
    'version': '0.1.0a0',
    'description': 'Extract data from manga sites',
    'long_description': None,
    'author': 'nhanb',
    'author_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
