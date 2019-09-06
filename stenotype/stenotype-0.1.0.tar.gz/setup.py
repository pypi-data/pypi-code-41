# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['stenotype']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'stenotype',
    'version': '0.1.0',
    'description': 'Support for shorthand type annotations.',
    'long_description': 'stenotype\n=========\n\n\n.. header-end\n\nDevelopment Quickstart\n----------------------\nThis project uses poetry_ for dependency management, so please make sure\n`it is installed`_ on your work station. If it is, you should first run\n``poetry install`` in the project root, and after entering your fresh new\nvirtual environment with ``poetry shell`` you are ready to go.\n\n\nProject Description\n-------------------\n\n.. put your project description here\n\n.. _poetry: https://poetry.eustace.io/\n.. _it is installed: https://poetry.eustace.io/docs/#installation',
    'author': 'Arne Recknagel',
    'author_email': 'arne.recknagel@hotmail.com',
    'url': 'https://github.com/a-recknagel/stenotype',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
