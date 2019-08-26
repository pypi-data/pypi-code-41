# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pycaprio',
 'pycaprio.core',
 'pycaprio.core.adapters',
 'pycaprio.core.clients',
 'pycaprio.core.interfaces',
 'pycaprio.core.objects',
 'pycaprio.core.schemas']

package_data = \
{'': ['*']}

install_requires = \
['requests', 'tenacity>=5.1,<6.0']

setup_kwargs = {
    'name': 'pycaprio',
    'version': '0.0.1',
    'description': 'Python client for the INCEpTION annotation tool API',
    'long_description': None,
    'author': 'Savanamed',
    'author_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
