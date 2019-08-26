# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['portray']

package_data = \
{'': ['*'], 'portray': ['mkdocs_templates/partials/*', 'pdoc3_templates/*']}

install_requires = \
['GitPython>=3.0,<4.0',
 'hug>=2.5,<3.0',
 'mkdocs-material>=4.4,<5.0',
 'mkdocs>=1.0,<2.0',
 'pdoc3>=0.6.3,<0.7.0',
 'pymdown-extensions>=6.0,<7.0',
 'toml>=0.10.0,<0.11.0']

entry_points = \
{'console_scripts': ['portray = portray.cli:__hug__.cli']}

setup_kwargs = {
    'name': 'portray',
    'version': '1.0.5',
    'description': 'Your Project with Great Documentation',
    'long_description': None,
    'author': 'Timothy Crosley',
    'author_email': 'timothy.crosley@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
