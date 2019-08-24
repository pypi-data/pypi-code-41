# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['find_the_site']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.7.1,<5.0.0',
 'requests>=2.22,<3.0',
 'user-agent>=0.1.9,<0.2.0']

setup_kwargs = {
    'name': 'find-the-site',
    'version': '0.1.0',
    'description': 'Find the site in duckduckgo',
    'long_description': None,
    'author': 'serhii',
    'author_email': 'aserhii@protonmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
