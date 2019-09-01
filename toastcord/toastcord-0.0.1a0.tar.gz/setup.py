# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['toastcord']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'toastcord',
    'version': '0.0.1a0',
    'description': 'Collection of useful utilities for discord.py (and maybe Hikari :P)',
    'long_description': "# ToastCord\n\nCollection of useful utilities for discord.py (and maybe Hikari :P)\n\n\n### Credits\n\nA massive thanks to Espy (Nekoka.tt) for the amazing CI scripts and docs generation. All credit goes to him, as I've just did some tweaking. The files in question come from Hikari's [main](https://gitlab.com/nekokatt/hikari) and [core](https://gitlab.com/nekokatt/hikari.core) repositories.\n\n",
    'author': 'Tmpod',
    'author_email': 'tmpod@protonmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
