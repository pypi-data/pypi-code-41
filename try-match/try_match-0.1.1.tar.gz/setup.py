# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['try_match']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'try-match',
    'version': '0.1.1',
    'description': 'Pattern matching',
    'long_description': None,
    'author': 'Zhengyu Xu',
    'author_email': 'zen-xu@outlook.com',
    'url': 'https://github.com/zen-xu/try_match',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=2.7,<3.0',
}


setup(**setup_kwargs)
