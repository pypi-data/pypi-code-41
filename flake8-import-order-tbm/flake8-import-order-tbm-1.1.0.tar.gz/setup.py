# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['flake8_import_order_tbm']

package_data = \
{'': ['*']}

install_requires = \
['natsort>=5.0,<7.0']

extras_require = \
{':extra == "dev" or extra == "lint"': ['flake8>=3.5,<4.0',
                                        'flake8-import-order>=0.18,<0.19'],
 'dev': ['flake8-builtins>=1.0,<2.0',
         'flake8-comprehensions>=2.0,<3.0',
         'flake8-import-order-tbm>=1.0,<2.0',
         'nox>=2019,<2020'],
 'lint': ['flake8-builtins>=1.0,<2.0',
          'flake8-comprehensions>=2.0,<3.0',
          'flake8-import-order-tbm>=1.0,<2.0']}

entry_points = \
{'flake8_import_order.styles': ['tbm = flake8_import_order_tbm:TBM']}

setup_kwargs = {
    'name': 'flake8-import-order-tbm',
    'version': '1.1.0',
    'description': 'flake8-import-order style plugin for my (thebigmunch) taste.',
    'long_description': '# flake8-import-order-tbm\n\n[![PyPI](https://img.shields.io/pypi/v/flake8-import-order-tbm.svg?label=PyPI)](https://pypi.org/project/flake8-import-order-tbm/)\n![](https://img.shields.io/badge/Python-3.6%2B-blue.svg)  \n[![Travis](https://img.shields.io/travis/thebigmunch/flake8-import-order-tbm.svg?label=Travis)](https://travis-ci.org/thebigmunch/flake8-import-order-tbm)  \n\n[flake8-import-order-tbm](https://github.com/thebigmunch/flake8-import-order-tbm) is a style for\n[flake8-import-order](https://github.com/PyCQA/flake8-import-order).\n\n\n## Styling\n\n* Package, module, and imported names are naturally sorted using [natsort](https://github.com/SethMMorton/natsort).\n* Standard library import section precedes 3rd-party import section precedes local import section.\n* Import statements precede from import statements.\n* UPPERCASE precedes Capitalized precedes lowercase.\n* Fewer levels in a local relative import precede greater levels.\n\nA basic example:\n\n```\nimport os\nimport sys\nfrom os import path\n\nimport attr\nimport requests\nfrom attr import attrib, attrs\n\nimport LocalPackage\nimport localpackage\nfrom localpackage import name\nfrom . import name1, name2, name10\nfrom .module import name3\nfrom ..module import name4\n```\n\n## Usage\n\nInstall ``flake8-import-order-tbm`` using ``pip install flake8-import-order-tbm``.\n\nWhen running flake8, do one of the following:\n\n* Add the ``--import-order-style=tbm`` option to the command.\n\n* Add this to your [flake8 config](http://flake8.pycqa.org/en/latest/user/configuration.html):\n\n\t```\n\timport-order-style = tbm\n\t```\n',
    'author': 'thebigmunch',
    'author_email': 'mail@thebigmunch.me',
    'url': 'https://github.com/thebigmunch/flake8-import-order-tbm',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
