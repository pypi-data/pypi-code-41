# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['file_chooser']

package_data = \
{'': ['*']}

install_requires = \
['pygobject>=3.32.2,<4.0.0']

setup_kwargs = {
    'name': 'gtk-file-chooser',
    'version': '0.2.0',
    'description': 'A Simple Gtk File Chooser Dialog',
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
