# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['gerby', 'gerby.clients', 'gerby.data']

package_data = \
{'': ['*']}

install_requires = \
['cached_property>=1.5,<2.0',
 'numpy>=1.17,<2.0',
 'pandas>=0.25.0,<0.26.0',
 'requests>=2.22,<3.0',
 'slackclient==1.3.2']

setup_kwargs = {
    'name': 'gerby',
    'version': '0.1.1',
    'description': 'Core functionality for Very data analysis.',
    'long_description': None,
    'author': 'Jeff McGehee',
    'author_email': 'jeff@verypossible.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
