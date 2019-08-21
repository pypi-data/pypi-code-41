# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['portray']

package_data = \
{'': ['*']}

install_requires = \
['hug>=2.5,<3.0', 'mkdocs>=1.0,<2.0', 'pdoc3>=0.6.3,<0.7.0']

setup_kwargs = {
    'name': 'portray',
    'version': '0.0.1',
    'description': 'Your Project with Great Documentation',
    'long_description': None,
    'author': 'Timothy Crosley',
    'author_email': 'timothy.crosley@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
