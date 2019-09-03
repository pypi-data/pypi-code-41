# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['solid', 'solid.examples', 'solid.test']

package_data = \
{'': ['*'],
 'solid': ['.mypy_cache/3.7/*',
           '.mypy_cache/3.7/collections/*',
           '.mypy_cache/3.7/importlib/*',
           '.mypy_cache/3.7/os/*',
           '.mypy_cache/3.7/solid/*',
           '.vscode/*',
           'mypy/*',
           'mypy/.mypy_cache/3.7/*',
           'mypy/.mypy_cache/3.7/collections/*',
           'mypy/.mypy_cache/3.7/importlib/*',
           'mypy/.mypy_cache/3.7/os/*'],
 'solid.examples': ['Compiled_examples/*', 'mazebox/*'],
 'solid.test': ['solidpython.egg-info/*']}

install_requires = \
['PrettyTable==0.7.2',
 'euclid3>=0.1.0,<0.2.0',
 'pypng>=0.0.19,<0.0.20',
 'regex>=2019.4,<2020.0']

setup_kwargs = {
    'name': 'solidpython',
    'version': '0.4.1',
    'description': 'Python interface to the OpenSCAD declarative geometry language',
    'long_description': None,
    'author': 'Evan Jones',
    'author_email': 'evan_t_jones@mac.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
