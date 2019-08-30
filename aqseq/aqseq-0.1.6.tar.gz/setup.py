# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['aqseq', 'aqseq._version', 'aqseq.connectors']

package_data = \
{'': ['*'], 'aqseq': ['archived/*']}

install_requires = \
['benchlingapi>=2.0.0a0,<3.0.0',
 'bs4>=0.0.1,<0.0.2',
 'inflection>=0.3.1,<0.4.0',
 'jdna>=0.1.2,<0.2.0',
 'loggable-jdv>=0.1.2,<0.2.0',
 'pydent==0.1.5a6',
 'requests>=2.22,<3.0',
 'urlopen>=1.0,<2.0']

entry_points = \
{'console_scripts': ['name = aqseq:_version.get_name',
                     'upver = aqseq:_version.pull_version',
                     'version = aqseq:_version.get_version']}

setup_kwargs = {
    'name': 'aqseq',
    'version': '0.1.6',
    'description': 'sequence manager for Aquarium and Benchling',
    'long_description': '# AqSequenceManager\n\nConvinience methods for managing DNA sequences between the Aquarium LIMS and Benchling.\n',
    'author': 'Justin Vrana',
    'author_email': 'justin.vrana@gmail.com',
    'url': 'https://www.github.com/jvrana/AqSequenceManager',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
