# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cp2k_input_tools']

package_data = \
{'': ['*']}

install_requires = \
['transitions>=0.7.0,<0.8.0']

entry_points = \
{'console_scripts': ['cp2klint = cp2k_input_tools.cli:cp2klint',
                     'fromcp2k = cp2k_input_tools.cli:fromcp2k',
                     'tocp2k = cp2k_input_tools.cli:tocp2k']}

setup_kwargs = {
    'name': 'cp2k-input-tools',
    'version': '0.1.0',
    'description': 'Python tools to handle CP2K input files',
    'long_description': "# cp2k-input-tools\n\n[![Build Status](https://travis-ci.com/dev-zero/cp2k-input-tools.svg?branch=develop)](https://travis-ci.com/dev-zero/cp2k-input-tools) [![codecov](https://codecov.io/gh/dev-zero/cp2k-input-tools/branch/develop/graph/badge.svg)](https://codecov.io/gh/dev-zero/cp2k-input-tools)\n\nFully validating pure-python CP2K input file parsers including preprocessing capabilities\n\nAvailable commands:\n\n* `cp2klint` .. a CP2K input file linter\n* `fromcp2k` .. create a JSON or YAML configuration file from a CP2K input file\n* `tocp2k` .. convert a JSON or YAML configuration back to CP2K's input file format\n\n## Requirements\n\n* Python 3.6+\n* https://pypi.org/project/transitions/\n\nFor development: https://poetry.eustace.io/\n\n## Idea\n\n* have a pure-python CP2K input file linter with proper syntax error reporting (context, etc.)\n* a final & complete restart file parser\n* basis for an AiiDA CP2K project importer\n* testbed for alternative import formats (YAML, JSON) for CP2K\n* possible testbed for a re-implementation of the CP2K input parser itself\n\n## TODOs\n\n* [ ] parser: improve error reporting with context (tokenizer/preprocessor is already done)\n* [ ] preprocessor: losing original context when replacing variables\n* [ ] parser: unit conversion of values\n* [ ] parser: parsing the XML is sloooow (easily 70% of the time), pickle or generate Python code directly instead and keep XML parsing as backup?\n",
    'author': 'Tiziano Müller',
    'author_email': 'tiziano.mueller@chem.uzh.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
