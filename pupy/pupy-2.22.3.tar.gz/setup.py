# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pupy']

package_data = \
{'': ['*']}

extras_require = \
{'io': ['toml>=0.10.0,<0.11.0',
        'python-rapidjson>=0.7.2,<0.8.0',
        'msgpack>=0.6.1,<0.7.0',
        'ruamel.yaml>=0.15.97,<0.16.0',
        'aiofiles>=0.4.0,<0.5.0']}

entry_points = \
{'console_scripts': ['pupy = pupy.cli:main']}

setup_kwargs = {
    'name': 'pupy',
    'version': '2.22.3',
    'description': 'pretty useful python',
    'long_description': "# PUPY ~ Pretty Useful Python\n\nThis package (pupy) is full of Pretty Useful Python.\n\n## These things\n\n[![Build Status](https://travis-ci.org/jessekrubin/pupy.svg?branch=master)](https://travis-ci.org/jessekrubin/pupy) \n[![Wheel](https://img.shields.io/pypi/wheel/pupy.svg)](https://img.shields.io/pypi/wheel/pupy.svg) \n[![Version](https://img.shields.io/pypi/v/pupy.svg)](https://img.shields.io/pypi/v/pupy.svg) \n[![py_versions](https://img.shields.io/pypi/pyversions/pupy.svg)](https://img.shields.io/pypi/pyversions/pupy.svg) \n \n\n## Installin'\n\nInstalling is EZPZ...\n\n    pip install pupy\n\n### Want more???\n\nPupy has a few optional dependenies for reading and writing files which can be installed with the following command:\n    \n    pip install pupy[io]\n\nOr you can pick and choose...\n\nIf you plan on using Jason you can install `ujson` \n\n    pip install ujson \n    \nor `rapidjson` for a speed boost \n\n    pip install python-rapidjson\n\nand if pupy can't find either it'll fall back on the python-stdlib json thing.\n\nBut wait theres more! Pupy has several optional dependencies for savings and loads which you can install with...\n    \n    pip install ruamel.yaml  # If ya mel in your spare time\n    pip install msgpack  # If you wanna pack messages\n    pip install toml  # toml (aka 'that other markup language'(?))\n    pip install aiofiles  # if you wanna do async stuff\n\n## Testimonials\n\n*'Ahead of the curve.' -Haley who goes to Harvard*\n\n*'huh?' -Tim Apple*\n\n*'If I were stranded on a dessert island and had to pick between having a copy pupy or a thing of water I would pick the water, but if I didn't have to pick it wouldn't hurt to have.' -Ryan of the fro with his fro*\n\n*'I don't use python.' -KirstenKirsten Chief Evernote Officer*\n\n*'I can't say google wouldn't not go down if it weren't for pupy.' -Ben W from the g-suite*\n\n*'A literary masterpiece on par with my second greatest work finite jest.' -Bananas Foster Wallace*\n\n*'Best place for python savings and loads in the tri-content area.' -Genghis Khan*\n\n\n",
    'author': 'jessekrubin',
    'author_email': 'jessekrubin@gmail.com',
    'url': 'https://github.com/jessekrubin/pupy',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
