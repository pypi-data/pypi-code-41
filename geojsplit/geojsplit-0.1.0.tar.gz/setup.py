# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['geojsplit']

package_data = \
{'': ['*']}

install_requires = \
['geojson>=2.5,<3.0', 'ijson>=2.4,<3.0', 'simplejson>=3.16,<4.0']

extras_require = \
{'docs': ['sphinx>=2.2,<3.0', 'sphinx_rtd_theme>=0.4.3,<0.5.0']}

entry_points = \
{'console_scripts': ['geojsplit = geojsplit.cli:main']}

setup_kwargs = {
    'name': 'geojsplit',
    'version': '0.1.0',
    'description': 'A python implementation of the npm package geojsplit. Used to split GeoJSON files into smaller pieces.',
    'long_description': None,
    'author': 'Yann-Sebastien Tremblay-Johnston',
    'author_email': 'yanns.tremblay@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
