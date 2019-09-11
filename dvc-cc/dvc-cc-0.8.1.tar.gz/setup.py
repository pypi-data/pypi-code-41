# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dvc_cc',
 'dvc_cc.cancel',
 'dvc_cc.git',
 'dvc_cc.hyperopt',
 'dvc_cc.init',
 'dvc_cc.live_output',
 'dvc_cc.output_to_tmp',
 'dvc_cc.output_to_tmp_fast',
 'dvc_cc.run',
 'dvc_cc.run_all_defined',
 'dvc_cc.setting',
 'dvc_cc.status']

package_data = \
{'': ['*']}

install_requires = \
['cc-faice>=8.0,<9.0',
 'dvc>=0,<1',
 'keyring>=19.0,<20.0',
 'matplotlib>=3.1,<4.0',
 'nbconvert>=5.5,<6.0',
 'numpy>=1.16,<2.0',
 'pandas>=0,<1',
 'paramiko>=2.4,<3.0',
 'pyrsistent>=0.15.2,<0.16.0',
 'python-gitlab>=1.8,<2.0',
 'pyyaml>=5.1,<6.0',
 'seaborn>=0,<1']

entry_points = \
{'console_scripts': ['dvc-cc = dvc_cc.main:main']}

setup_kwargs = {
    'name': 'dvc-cc',
    'version': '0.8.1',
    'description': 'This connector is used to combine the work of CC (www.curious-containers.cc) and DVC (Open-source Version Control System for Machine Learning Projects).',
    'long_description': '# The DVC-CC client\nIn this subrepository the [DVC-CC](https://github.com/deep-projects/dvc-cc) client is defined. The client is needed to define hyper optimization and push your jobs to [Curious Containers CC](https://www.curious-containers.cc/).\n\n## Get started\nTODO\n\n### Overview\nTODO\n\n### Tutorials\n- [An old tutorial](https://github.com/deep-projects/dvc-cc/blob/master/dvc-cc/tutorial/SimpleStart.md)\n\n\n## Acknowledgements\nThe DVC-CC software is developed at CBMI (HTW Berlin - University of Applied Sciences). The work is supported by the\nGerman Federal Ministry of Education and Research (project deep.TEACHING, grant number 01IS17056 and project\ndeep.HEALTH, grant number 13FH770IX6).',
    'author': 'Jonas Annuscheit',
    'author_email': 'annusch@htw-berlin.de',
    'url': 'https://github.com/mastaer/dvc-cc.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
