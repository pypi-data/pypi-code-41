# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['black_mamba', 'black_mamba.deploy', 'black_mamba.testlib']

package_data = \
{'': ['*'],
 'black_mamba': ['compilation/*',
                 'compilation/compiled_files/*',
                 'initialization/*',
                 'initialization/init_files/*']}

install_requires = \
['eth-tester==0.1.0b32',
 'py-evm==0.2.0a41',
 'pytest>=5.1,<6.0',
 'vyper==0.1.0b12',
 'web3==4.7.2']

entry_points = \
{'console_scripts': ['mamba = black_mamba:mamba_cli:parse_cli_args']}

setup_kwargs = {
    'name': 'black-mamba',
    'version': '0.1.0',
    'description': 'Development framework to write, test and deploy smart contracts written in Vyper.',
    'long_description': '# mamba\nA framework for developing smart contracts in Vyper.\n',
    'author': 'Arjuna Sky Kok',
    'author_email': 'arjuna@mamba.black',
    'url': 'https://mamba.black',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
