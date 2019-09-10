# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['whippet']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['whippet = whippet:console.main']}

setup_kwargs = {
    'name': 'whippet',
    'version': '0.2.2',
    'description': 'Install make based hooks with ease.',
    'long_description': 'Whippet - like husky, but leaner\n################################\nA simple git hooks installer. Inspired by husky_.\n\n.. _husky: https://github.com/typicode/husky#readme\n',
    'author': 'Dalibor Novak',
    'author_email': 'BorePlusPlus@gmail.com',
    'url': 'https://github.com/BorePlusPlus/whippet',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
