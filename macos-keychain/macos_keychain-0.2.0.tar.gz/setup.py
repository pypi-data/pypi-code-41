# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['macos_keychain']

package_data = \
{'': ['*']}

install_requires = \
['sh>=1.12,<2.0']

setup_kwargs = {
    'name': 'macos-keychain',
    'version': '0.2.0',
    'description': 'A Simple MacOS Keychain Store',
    'long_description': "# macos_keychain\n\nMacOS keychain password manager\n\n## Adding a password to keychain\n\n```python\nimport macos_keychain\n\nmacos_keychain.add(name='API token', value='<TOKEN>')\n```\n\n## Removing passwords in keychain\n\n```python\nimport macos_keychain\n\nmacos_keychain.rm(name='API token')\n```\n\n## Listing passwords in keychain\n\n```python\nimport macos_keychain\n\nmacos_keychain.ls()\n```\n\n## Getting password in keychain\n```python\nimport macos_keychain\n\nmacos_keychain.get(name='API token')\n```\n",
    'author': 'Juan Gonzalez',
    'author_email': 'jrg2156@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
