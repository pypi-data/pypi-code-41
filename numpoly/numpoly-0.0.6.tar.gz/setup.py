# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['numpoly']

package_data = \
{'': ['*']}

install_requires = \
['numpy']

setup_kwargs = {
    'name': 'numpoly',
    'version': '0.0.6',
    'description': 'Polynomials as a numpy datatype',
    'long_description': 'Numpoly is a generic library for creating, manipulating polynomial arrays.\n\n``numpoly`` is a subclass of ``numpy.ndarray`` and as such is compatible with\nmost ``numpy`` functions, where that makes sense.\n\n|circleci| |codecov|\n\n.. |circleci| image:: https://circleci.com/gh/jonathf/numpoly/tree/master.svg?style=shield\n    :target: https://circleci.com/gh/jonathf/numpoly/tree/master\n.. |codecov| image:: https://codecov.io/gh/jonathf/numpoly/branch/master/graph/badge.svg\n    :target: https://codecov.io/gh/jonathf/numpoly\n\nInstallation\n------------\n\nInstallation should be straight forward::\n\n    pip install numpoly\n\nAnd you should be ready to go.\n',
    'author': 'Jonathan Feinberg',
    'author_email': 'jonathf@gmail.com',
    'url': 'https://github.com/jonathf/numpoly',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
}


setup(**setup_kwargs)
