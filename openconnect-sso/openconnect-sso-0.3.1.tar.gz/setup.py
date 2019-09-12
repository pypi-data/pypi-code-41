# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['openconnect_sso', 'openconnect_sso.browser']

package_data = \
{'': ['*']}

install_requires = \
['PyQt5>=5.12,<6.0',
 'PyQtWebEngine>=5.12,<6.0',
 'attrs>=18.2,<19.0',
 'colorama>=0.4,<0.5',
 'keyring>=18.0,<19.0',
 'lxml>=4.3,<5.0',
 'prompt-toolkit>=2.0,<3.0',
 'pyxdg>=0.26,<0.27',
 'requests>=2.22,<3.0',
 'structlog>=19.1,<20.0',
 'toml>=0.10,<0.11']

entry_points = \
{'console_scripts': ['openconnect-sso = openconnect_sso.cli:main']}

setup_kwargs = {
    'name': 'openconnect-sso',
    'version': '0.3.1',
    'description': 'Wrapper script for OpenConnect supporting Azure AD (SAMLv2) authentication',
    'long_description': '# openconnect-sso\nWrapper script for OpenConnect supporting Azure AD (SAMLv2) authentication\n\n## TL; DR\n```bash\n$ pip install openconnect-sso-$VERSION.whl\n$ openconnect-sso --server vpn.server.com/group\n```\n\n## Configuration\nIf you want to save credentials and get them automatically\ninjected in the web browser:\n```bash\n$ openconnect-sso --server vpn.server.com/group --user user@domain.com\nPassword (user@domain.com): \n[info     ] Authenticating to VPN endpoint ...\n```\n\nUser credentials are automatically saved to the users login keyring (if available).\n\nIf you already have Cisco Anyconnect set-up, then `--server` argument is optional.\nAlso, the last used `--server` address is saved between sessions so there is no need\nto always type in the same arguments:\n\n```bash\n$ openconnect-sso\n[info     ] Authenticating to VPN endpoint ...\n```\n\nConfiguration is saved in `$XDG_CONFIG_HOME/openconnect-sso/config.toml`. On typical\nLinux installations it is located under `$HOME/.configopenconnect-sso/config.toml`\n',
    'author': 'László Vaskó',
    'author_email': 'laszlo.vasko@outlook.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
