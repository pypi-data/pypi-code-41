# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['snapaddy']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'snapaddy',
    'version': '0.0.0',
    'description': '',
    'long_description': '# snapADDY\n',
    'author': 'snapADDY GmbH',
    'author_email': 'info@snapaddy.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://snapaddy.com',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
