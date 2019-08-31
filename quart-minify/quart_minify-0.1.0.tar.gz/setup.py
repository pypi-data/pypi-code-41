# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['quart_minify']

package_data = \
{'': ['*']}

install_requires = \
['htmlmin>=0.1.12,<0.2.0',
 'jsmin>=2.2,<3.0',
 'lesscpy>=0.13.0,<0.14.0',
 'quart>=0.10.0,<0.11.0']

setup_kwargs = {
    'name': 'quart-minify',
    'version': '0.1.0',
    'description': 'A Quart extension to minify quart response for html, javascript, css and less compilation as well.',
    'long_description': None,
    'author': 'Mohamed Feddad',
    'author_email': 'mrf345@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
