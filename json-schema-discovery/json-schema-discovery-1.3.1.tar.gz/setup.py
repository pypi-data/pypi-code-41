# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['json_schema_discovery']

package_data = \
{'': ['*']}

install_requires = \
['tabulate>=0.8.3,<0.9.0']

setup_kwargs = {
    'name': 'json-schema-discovery',
    'version': '1.3.1',
    'description': 'Database-agnostic JSON schema discovery',
    'long_description': 'Database-agnostic JSON schema discovery\n\nCreate and merge json schemas, with occurence counting\n\n\nQuickstart\n----------\n\nStart with ``Empty`` or using ``make_schema()`` and merge with json-like python objects using ``+=``\n\nVisualize the resulting schema with ``dumps()`` or by printing the object\n\nGet a sense of the overall structure with ``statistics()``\n',
    'author': 'Stepland',
    'author_email': 'Stepland@hotmail.fr',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
