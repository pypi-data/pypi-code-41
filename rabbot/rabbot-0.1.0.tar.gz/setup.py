# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['rabbot']

package_data = \
{'': ['*']}

install_requires = \
['black>=18.3-alpha.0,<19.0', 'pika>=1.1,<2.0']

entry_points = \
{'console_scripts': ['rabbot = rabbot.rabbot:main']}

setup_kwargs = {
    'name': 'rabbot',
    'version': '0.1.0',
    'description': 'A small utility for testing RabbitMQ connections.',
    'long_description': '# Rabbot\n\n[![Build Status](https://cloud.drone.io/api/badges/dsudduth/rabbot/status.svg)](https://cloud.drone.io/dsudduth/rabbot)\n\nA utility for validating connections to RabbitMQ servers.\n\n## Installing Rabbot\n\n```bash\npip install rabbot\n```\n\n## Development\n\nThis project relies on [Poetry](https://poetry.eustace.io/) for development, packaging, and publishing. You will need to have this tool installed on your machine before you can properly develop against Rabbot.\n\n```bash\ncurl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python\n```\n\nPlease see the [installation](https://poetry.eustace.io/docs/#installation) guide for other options.\n\n\n## Contributing\n\nSee [CONTRIBUTING.md](CONTRIBUTING.md).\n\n## Versioning\n\nThis project uses semantic versioning ([SemVer 2.0.0](https://semver.org/)). Incrementing versions is managed by [bumpversion](https://github.com/peritus/bumpversion).\n\nTo ensure that the repo is properly versioned, you will need to install `bumpversion`.\n\n```bash\npip install bumpversion\n```\n\nOnce installed, bump the version before pushing your code or created a pull request.\n\n```bash\n# Examples\n\n# Bumping the major version to indicate a backwards incompatible change\nbumpversion major\n\n# Bumping the minor version\nbumpversion minor\n\n# Bumping the subminor due to a hotfix\nbumpversion patch\n```\n\n*Note: Bumpversion is configured to automatically create a commit when executed.*\n',
    'author': 'Derek Sudduth',
    'author_email': 'derek.sudduth@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
