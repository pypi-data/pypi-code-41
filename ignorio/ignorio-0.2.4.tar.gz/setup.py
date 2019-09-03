# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['ignorio']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0', 'colorama>=0.3.9,<0.4.0', 'requests>=2.19,<3.0']

entry_points = \
{'console_scripts': ['ig = ignorio.cli:main']}

setup_kwargs = {
    'name': 'ignorio',
    'version': '0.2.4',
    'description': 'Manage your .gitignore with ease!',
    'long_description': '# Ignorio\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ignorio.svg) ![PyPI](https://img.shields.io/pypi/v/ignorio.svg) [![Build Status](https://travis-ci.org/franccesco/ignorio.svg?branch=master)](https://travis-ci.org/franccesco/ignorio) [![Coverage Status](https://coveralls.io/repos/github/franccesco/ignorio/badge.svg?branch=master)](https://coveralls.io/github/franccesco/ignorio?branch=master) ![GitHub](https://img.shields.io/github/license/franccesco/ignorio.svg) [![Twitter](https://img.shields.io/twitter/url/https/github.com/franccesco/ignorio.svg?style=social)](https://twitter.com/intent/tweet?text=Wow:&url=https%3A%2F%2Fgithub.com%2Ffranccesco%2Fignorio)\n\n**Ignorio** is a simple package to manage your [git exclusions](https://git-scm.com/docs/gitignore). This command line application helps you to download a template from [gitignore.io](http://gitignore.io/) without going to the site using the site\'s [API](https://www.gitignore.io/api/) \n\n# Usage\n\n## Add a language exclusion list\n* You can add multiple languages to the exclusions list, just make sure they\'re listed on the supported list.\n\n![](assets/add_lang.png)\n\n## Append a language to the exclusion list\n* You don\'t have to overwrite your current exclusion list, if you have added Python and SublimeText before then you can go right ahead and append Ruby to it.\n\n![](assets/append_lang.png)\n\n## Show supported languages\n* Supported list of languages by gitignore.io, you can easily grep this data if you need to find a determined language.\n\n![](assets/show_supported.png)\n\n## Verbose for the paranoids\n* And if you\'re paranoid enough or just like to see more data displayed on your terminal, well, check the `-v` flag.\n\n![](assets/verbosity.png)\n\n# How to contribute\n* Fork it\n* Make changes\n* Make a pull request to the **develop** branch.\n\n# Like the project?\nIf you like the project and would like to chip in a dolar or two, go ahead and do it here.\n\n<a href="https://www.paypal.me/orozcofranccesco">\n  <img height="32" src="assets/paypal_badge.png" />\n</a> <a href="https://www.buymeacoffee.com/franccesco" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/white_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a> <a href=\'https://ko-fi.com/V7V8AXFE\' target=\'_blank\'><img height=\'36\' style=\'border:0px;height:36px;\' src=\'https://az743702.vo.msecnd.net/cdn/kofi2.png?v=0\' border=\'0\' alt=\'Buy Me a Coffee at ko-fi.com\' /></a>\n',
    'author': 'Franccesco Orozco',
    'author_email': 'franccesco@codingdose.info',
    'url': 'https://github.com/franccesco/ignorio',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
