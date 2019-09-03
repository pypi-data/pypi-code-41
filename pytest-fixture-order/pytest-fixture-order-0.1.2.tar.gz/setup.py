# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pytest_fixture_order']

package_data = \
{'': ['*']}

install_requires = \
['pytest>=3.0']

entry_points = \
{'pytest11': ['fixture_order = pytest_fixture_order.plugin']}

setup_kwargs = {
    'name': 'pytest-fixture-order',
    'version': '0.1.2',
    'description': 'pytest plugin to control fixture evaluation order',
    'long_description': '# pytest-fixture-order\nUse markers to control the order in which fixtures are evaluated.\n',
    'author': 'Zach "theY4Kman" Kanzler',
    'author_email': 'z@perchsecurity.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
