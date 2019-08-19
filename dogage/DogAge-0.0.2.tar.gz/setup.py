# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['DogAge']

package_data = \
{'': ['*']}

install_requires = \
['argparse', 'matplotlib', 'numpy', 'pandas', 'sklearn']

entry_points = \
{'console_scripts': ['dogage_validate = DogAge:dogage_validate.main']}

setup_kwargs = {
    'name': 'dogage',
    'version': '0.0.2',
    'description': 'Programms for DogAge Challenge',
    'long_description': None,
    'author': 'Aleksandr Sinitca',
    'author_email': 'siniza.s.94@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
