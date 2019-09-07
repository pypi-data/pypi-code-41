# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['datetime_popover']

package_data = \
{'': ['*']}

install_requires = \
['pygobject>=3.32.2,<4.0.0']

setup_kwargs = {
    'name': 'gtk-datetime-popover',
    'version': '0.3.0',
    'description': 'A Gtk Popover widget for handling dates and times',
    'long_description': None,
    'author': 'BeatLink',
    'author_email': 'beatlink@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
