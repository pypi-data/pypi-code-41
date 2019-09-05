# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['migrark', 'migrark.collector', 'migrark.models', 'migrark.versioner']

package_data = \
{'': ['*']}

install_requires = \
['psycopg2>=2.8,<3.0']

setup_kwargs = {
    'name': 'migrark',
    'version': '0.2.0',
    'description': 'Migration Management Library',
    'long_description': None,
    'author': 'Esteban Echeverry',
    'author_email': 'eecheverry@nubark.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
