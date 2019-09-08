# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['po_publish']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['po-publish = po_publish.script:main']}

setup_kwargs = {
    'name': 'po-publish',
    'version': '0.1.0',
    'description': 'wraps `poetry publish --build` with some logic for my personal needs',
    'long_description': 'wraps `poetry publish --build` with some logic for my personal needs\n',
    'author': 'Philip Olson',
    'author_email': 'philip.olson@pm.me',
    'url': 'https://github.com/olsonpm/py_publish',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
