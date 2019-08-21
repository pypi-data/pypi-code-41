# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['python_aws_ssm']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.9,<2.0']

setup_kwargs = {
    'name': 'python-aws-ssm',
    'version': '0.1.1',
    'description': 'Python package that interfaces with AWS System Manager',
    'long_description': '![build](https://action-badges.now.sh/PaddleHQ/python-aws-ssm)\n[![codecov](https://codecov.io/gh/PaddleHQ/python-aws-ssm/branch/master/graph/badge.svg)](https://codecov.io/gh/PaddleHQ/python-aws-ssm)\n[![license](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)\n[![codestyle](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\n# python-aws-ssm\nPython package that interfaces with [AWS System Manager](https://www.amazonaws.cn/en/systems-manager/).\n\n## Why to use python-aws-ssm and not the boto3 SSM client?\nThis package is wrapping boto3 SSM client and hides the complexity dealing with the not so Python friendly AWS SDK.\nPerfect use case for this package is when secure parameters for an application are stored to\n[AWS Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)\nusing a path hierarchy. During application startup you can use this package to fetch them and use them in your application.\n\n## Warning\n\nThe SSM service is rate-limited by default. We strongly suggest using\nretrieving SSM keys by path, e.g. via `ParameterStore.get_parameters_by_path()`.\nThis requires grouping keys by a useful path but reduces the chance of\nyour own services being rate-limited in turn.\n\n## Install\n```bash\npip install aws-ssm\n```\n\n## Examples\n\n#### Basic Usage\n\n```python\nfrom aws_ssm.parameters import ParameterStore\n\n# Assuming you have the parameters in the following format:\n# my-service/dev/param-1  -> with value `a`\n# my-service/dev/param-2  -> with value `b`\nparameter_store = ParameterStore()\n# Requesting the base path\nparameters = parameter_store.get_parameters_by_path("/my-service/dev/")\n# And getting a specific value\nvalue = parameters.get("param-1")\n# value should be `a`\n```\n\n#### Recursive and nested options\n\n```python\nfrom aws_ssm.parameters import ParameterStore\n\n# Assuming you have the parameters in the following format:\n# my-service/dev/param-1  -> with value `a`\n# my-service/dev/param-2  -> with value `b`\nparameter_store = ParameterStore()\n# Requesting the base path\nparameters = parameter_store.get_parameters_by_path(\n    "/my-service/", recursive=True, nested=True\n)\n# And getting a specific value\ndev_parameters = parameters.get("dev")\n# value should be {"param-1": "a", "param-2": "b"}\n```\n\n#### Get parameters by name\n\n```python\nfrom aws_ssm.parameters import ParameterStore\n\n# Assuming you have the parameters in the following format:\n# my-service/dev/param-1  -> with value `a`\n# common/dev/param-2  -> with value `b`\nparameter_store = ParameterStore()\n# Requesting the base path\nparameters = parameter_store.get_parameters(\n    ["/my-service/dev/param-1", "/common/dev/param-2"]\n)\n# And getting a specific value\ndev_parameters = parameters.get("/common/dev/param-2")\n# value should be `b`\n```\n\n#### With custom client\n\n```python\nfrom aws_ssm.parameters import ParameterStore\nimport boto3\n\n# Initialise an SSM client to specify the source of the credentials.\n# e.g. locally a profile would be more likely; an AWS Lambda would most\n# likely not override the credentials source.\nssm_client = boto3.Session(profile_name=\'dev\').client(\'ssm\')\nparameter_store = ParameterStore(ssm_client)\n\nparameters = parameter_store.get_parameters(["/service/path/"])\n```\n\n## Development\n\nIf you are missing any features or have found a bug, please open a PR or a new Github issue.\n\n\n#### Setup\nThis project uses Poetry to manage the dependencies and the virtual environment.\nFollow the instructions from Poetry website (https://poetry.eustace.io/docs/#installation) to configure your local environment.\n\nAfter completing the Poetry setup, the virtual environment can be created running:\n```shell\nmake setup\n```\n\n#### Tests\nTests are run by Pytest\n```shell\nmake test\n```\n\n#### Code style\n- Mypy is used for type annotations (https://github.com/python/mypy)\n- Black formatter (https://github.com/psf/black) is used to keep the coding style consistent.\n- Isort (https://github.com/timothycrosley/isort) is used to sort the imports.\nTo format the codebase just run:\n```shell\nmake format\n```\nand to check it before pushing:\n```shell\nmake lint\n```\n\n',
    'author': 'Luca Valentini',
    'author_email': 'luca@paddle.com',
    'url': 'https://github.com/PaddleHQ/python-aws-ssm',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
