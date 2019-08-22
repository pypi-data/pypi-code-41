# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['jrpyprogramming', 'jrpyprogramming.datasets']

package_data = \
{'': ['*'],
 'jrpyprogramming': ['vignettes/*'],
 'jrpyprogramming.datasets': ['data/*']}

install_requires = \
['matplotlib>=3.1,<4.0', 'numpy>=1.14.4,<2.0.0', 'pandas>=0.20.3,<0.24']

setup_kwargs = {
    'name': 'jrpyprogramming',
    'version': '0.1.8',
    'description': '',
    'long_description': None,
    'author': 'Jamie',
    'author_email': 'jamie@jumpingrivers.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
