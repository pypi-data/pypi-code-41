# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['makey']

package_data = \
{'': ['*']}

install_requires = \
['plumbum>=1.6.7,<2.0.0']

entry_points = \
{'console_scripts': ['makey = makey.__main__:main']}

setup_kwargs = {
    'name': 'makey',
    'version': '0.0.12',
    'description': 'Make libraries from GIT/url/tarball with CMAKE, and install using checkinstall.',
    'long_description': None,
    'author': 'Angus Hollands',
    'author_email': 'goosey15@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
