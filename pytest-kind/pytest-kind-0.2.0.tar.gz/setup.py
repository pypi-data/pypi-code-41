# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pytest_kind']

package_data = \
{'': ['*']}

install_requires = \
['pykube-ng>=0.30.0,<0.31.0']

entry_points = \
{'pytest11': ['pytest-kind = pytest_kind.plugin']}

setup_kwargs = {
    'name': 'pytest-kind',
    'version': '0.2.0',
    'description': 'Kubernetes test support with KIND for pytest',
    'long_description': '# pytest-kind\n\nTest your Python Kubernetes app/operator end-to-end with [kind](https://kind.sigs.k8s.io/).\n',
    'author': 'Henning Jacobs',
    'author_email': 'henning@jacobs1.de',
    'url': 'https://codeberg.org/hjacobs/pytest-kind',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
