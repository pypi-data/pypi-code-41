# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['reproserver', 'reproserver.repositories', 'reproserver.web']

package_data = \
{'': ['*'],
 'reproserver': ['static/css/*',
                 'static/fonts/*',
                 'static/js/*',
                 'templates/*']}

install_requires = \
['boto3>=1,<2',
 'jinja2',
 'psycopg2>=2.8,<3.0',
 'reprounzip-docker>=1.1,<2.0',
 'reprounzip>=1.1,<2.0',
 'sqlalchemy>=1,<2',
 'tornado>=5.0']

entry_points = \
{'console_scripts': ['reproserver = reproserver.main:main']}

setup_kwargs = {
    'name': 'reproserver',
    'version': '0.7',
    'description': 'A web application reproducing ReproZip packages in the cloud. Runs on Kubernetes',
    'long_description': '.. image:: https://img.shields.io/badge/chat-matrix.org-blue.svg\n   :alt: Matrix\n   :target: https://riot.im/app/#/room/#reprozip:matrix.org\n\nReproServer\n===========\n\nGoals\n-----\n\n- Import something we can build a Docker image from (currently only a ReproZip package)\n- Build a Docker image from it\n- Allow the user to change experiment parameters and input files\n- Run the experiment\n- Show the log and output files to the user\n',
    'author': 'Remi Rampin',
    'author_email': 'r@remirampin.com',
    'url': 'https://server.reprozip.org/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
