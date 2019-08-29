# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['yaenv']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'yaenv',
    'version': '1.0.0',
    'description': 'Yet another dotenv parser for Python.',
    'long_description': 'yaenv\n=====\n\n|pypi| |rtd| |travis|\n\n.. |pypi| image:: https://img.shields.io/pypi/v/yaenv.svg?logo=python\n   :target: https://pypi.org/project/yaenv/\n   :alt: PyPI\n\n.. |rtd| image:: https://img.shields.io/readthedocs/yaenv.svg?logo=read-the-docs\n   :target: https://yaenv.readthedocs.io/en/latest/\n   :alt: Read the Docs\n\n.. |travis| image:: https://img.shields.io/travis/ObserverOfTime/yaenv.svg?logo=travis\n   :target: https://travis-ci.org/ObserverOfTime/yaenv\n   :alt: Travis CI\n\nBecause none of the dozen dotenv parsers for Python fit all my use cases.\n\nInstallation\n------------\n\n.. code:: sh\n\n   pip install yaenv\n\nUsage\n-----\n\nDocumentation and examples are available on\n`Read the Docs <https://yaenv.rtfd.io>`_.\n\nSimilar projects\n----------------\n\n* `python-dotenv <https://github.com/theskumar/python-dotenv>`_\n* `django-environ <https://github.com/joke2k/django-environ>`_\n* `django-dotenv <https://github.com/jpadilla/django-dotenv>`_\n* `environs <https://github.com/sloria/environs>`_\n* `envparse <https://github.com/rconradharris/envparse>`_\n\nLicense\n-------\n\n`BSD 3-Clause License <LICENSE>`_\n',
    'author': 'ObserverOfTime',
    'author_email': 'chronobserver@disroot.org',
    'url': 'https://github.com/ObserverOfTime/yaenv',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.5',
}


setup(**setup_kwargs)
