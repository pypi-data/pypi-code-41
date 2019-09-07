# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['roax']

package_data = \
{'': ['*']}

install_requires = \
['geomet>=0.2,<0.3', 'roax>=1.9,<2.0']

setup_kwargs = {
    'name': 'roax-geo',
    'version': '1.1.1',
    'description': 'Geographic extension for Roax.',
    'long_description': '# Roax-Geo\n\n[![PyPI](https://badge.fury.io/py/roax-geo.svg)](https://badge.fury.io/py/roax-geo)\n[![License](https://img.shields.io/github/license/roax/roax-geo.svg)](https://github.com/roax/roax-geo/blob/master/LICENSE)\n[![GitHub](https://img.shields.io/badge/github-master-blue.svg)](https://github.com/roax/roax-geo/)\n[![Travis CI](https://travis-ci.org/roax/roax-geo.svg?branch=master)](https://travis-ci.org/roax/roax-geo)\n[![Codecov](https://codecov.io/gh/roax/roax-geo/branch/master/graph/badge.svg)](https://codecov.io/gh/roax/roax-geo)\n[![Black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)\n\nRoax-Geo: Geographical extension for Roax. \n\n## Develop\n\n```\npoetry install\npoetry run pre-commit install\n```\n\n## Test\n\n```\npoetry run pytest\n```\n',
    'author': 'Paul Bryan',
    'author_email': 'pbryan@anode.ca',
    'url': 'https://github.com/roax/roax-geo/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<3.8',
}


setup(**setup_kwargs)
