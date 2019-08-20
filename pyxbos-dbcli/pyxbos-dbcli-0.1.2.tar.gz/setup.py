# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pyxbos_dbcli']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.17,<2.0', 'prompt_toolkit>=2.0,<3.0', 'pygments>=2.4,<3.0']

setup_kwargs = {
    'name': 'pyxbos-dbcli',
    'version': '0.1.2',
    'description': '',
    'long_description': None,
    'author': 'Gabe Fierro',
    'author_email': 'gtfierro225@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
