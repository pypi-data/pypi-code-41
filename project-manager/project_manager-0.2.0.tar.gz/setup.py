# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['project_manager', 'project_manager.commands', 'project_manager.tests']

package_data = \
{'': ['*'], 'project_manager.tests': ['dummy_project/*']}

install_requires = \
['PyYAML>=5.1.2,<6.0.0',
 'anyconfig>=0.9.8,<0.10.0',
 'click>=7.0,<8.0',
 'pprint>=0.1.0,<0.2.0',
 'sh>=1.12,<2.0',
 'tqdm>=4.29,<5.0']

entry_points = \
{'console_scripts': ['project_manager = project_manager:cli']}

setup_kwargs = {
    'name': 'project-manager',
    'version': '0.2.0',
    'description': 'Easily run a project with various configuration setups',
    'long_description': '# project_manager\n\n[![pypi version](https://img.shields.io/pypi/v/project_manager.svg)](https://pypi.org/project/project_manager/)\n[![license](https://img.shields.io/pypi/l/project_manager.svg)](https://pypi.org/project/project_manager/)\n\nEasily run a project with various configuration setups.\n\n\n## Installation\n\n```bash\n$ pip install project_manager\n```\n\n\n## Usage\n\nAssuming that you have set up your [configuration file](https://project-manager.readthedocs.io/en/latest/setup_config.html) correctly,\na typical workflow could look like this:\n\n```bash\n$ project_manager build  # setup environment\n[..]\n$ project_manager run  # execute commands\n[..]\n$ project_manager gather  # aggregate results\n[..]\n```\n\nFor more information check out the [documentation](https://project-manager.readthedocs.io/).\n\n\n## Development notes\n\nRun tests:\n\n```bash\n$ pytest\n```\n\n\nPublish a new version to PyPi:\n\n```bash\n$ poetry --build publish\n```\n',
    'author': 'kpj',
    'author_email': 'kpjkpjkpjkpjkpjkpj@gmail.com',
    'url': 'https://github.com/kpj/project_manager',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
