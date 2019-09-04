# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['gmconfig']

package_data = \
{'': ['*']}

install_requires = \
['pyyaml>=5.1,<6.0']

setup_kwargs = {
    'name': 'gmconfig',
    'version': '0.2.3',
    'description': 'My lazy mans config loading and exporting module',
    'long_description': '# GMConfig\n\n[![PyPI version](https://badge.fury.io/py/gmconfig.svg)](https://badge.fury.io/py/gmconfig)\n\nMy lazy mans config loading and exporting module\n\n## Build\n\n```bash\npoetry build\n```\n',
    'author': 'GeekMasher',
    'author_email': None,
    'url': 'https://github.com/GeekMasher/GMConfig',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
