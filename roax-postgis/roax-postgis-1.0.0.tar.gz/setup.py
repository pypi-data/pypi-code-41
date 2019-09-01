# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['roax']

package_data = \
{'': ['*']}

install_requires = \
['roax-geo>=1.1,<2.0', 'roax-postgresql>=1.1,<2.0']

setup_kwargs = {
    'name': 'roax-postgis',
    'version': '1.0.0',
    'description': 'PostGIS extension for Roax.',
    'long_description': '# roax-postgis\n\n[![PyPI](https://badge.fury.io/py/roax-postgis.svg)](https://badge.fury.io/py/roax-postgis)\n[![License](https://img.shields.io/github/license/roax/roax-postgis.svg)](https://github.com/roax/roax-postgis/blob/master/LICENSE)\n[![GitHub](https://img.shields.io/badge/github-master-blue.svg)](https://github.com/roax/roax-postgis/)\n[![Travis CI](https://travis-ci.org/roax/roax-postgis.svg?branch=master)](https://travis-ci.org/roax/roax-postgis)\n[![Codecov](https://codecov.io/gh/roax/roax-postgis/branch/master/graph/badge.svg)](https://codecov.io/gh/roax/roax-postgis)\n[![Black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)\n\nPostGIS extension for Roax. \n',
    'author': 'Paul Bryan',
    'author_email': 'pbryan@anode.ca',
    'url': 'https://github.com/roax/roax-postgis/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<3.8',
}


setup(**setup_kwargs)
