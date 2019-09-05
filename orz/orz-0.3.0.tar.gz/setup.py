# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['orz']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'orz',
    'version': '0.3.0',
    'description': 'Result(Either) library for handling errors in monadic way',
    'long_description': None,
    'author': 'Yen, Tzu-Hsi',
    'author_email': 'joseph.yen@gmail.com',
    'url': 'https://github.com/d2207197/orz',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
}


setup(**setup_kwargs)
