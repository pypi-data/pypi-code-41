# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['ccompose']

package_data = \
{'': ['*'], 'ccompose': ['templates/*']}

install_requires = \
['click>=7.0,<8.0', 'jinja2>=2.10,<3.0', 'pyyaml>=5.1,<6.0']

entry_points = \
{'console_scripts': ['ccompose = ccompose.cli:cli',
                     'ccompose2mk = ccompose.cli:make_makefile_script',
                     'ccompose2sh = ccompose.cli:make_shell_script']}

setup_kwargs = {
    'name': 'ccompose',
    'version': '0.3.0',
    'description': 'Extended, drop in alternative to Docker-Compose',
    'long_description': None,
    'author': 'Olivier ORABONA',
    'author_email': 'oorabona@users.noreply.github.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
