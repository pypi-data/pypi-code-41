# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['asciinema_director']

package_data = \
{'': ['*']}

install_requires = \
['asciinema>=2.0,<3.0', 'click>=7.0,<8.0', 'pexpect>=4.7,<5.0']

entry_points = \
{'console_scripts': ['asciinema-director = asciinema_director:cli.cli']}

setup_kwargs = {
    'name': 'asciinema-director',
    'version': '0.1.1',
    'description': 'A way to record asciinema cast files like a pro.',
    'long_description': None,
    'author': 'Vinay Keerthi',
    'author_email': 'ktvkvinaykeerthi@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
