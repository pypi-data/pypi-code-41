# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['blackini']

package_data = \
{'': ['*']}

install_requires = \
['black>=19.3b0,<20.0']

entry_points = \
{'console_scripts': ['black = blackini.__main__:main']}

setup_kwargs = {
    'name': 'blackini',
    'version': '0.1.6',
    'description': '',
    'long_description': None,
    'author': 'Pablo Woolvett',
    'author_email': 'pablowoolvett@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
