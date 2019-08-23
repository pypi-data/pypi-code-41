# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': '.'}

packages = \
['strong_aws_lambda_contract_pkg']

package_data = \
{'': ['*']}

install_requires = \
['aws-lambda-context>=1.1,<2.0', 'dacite>=1.0,<2.0']

setup_kwargs = {
    'name': 'strong-aws-lambda.contract',
    'version': '0.1.0',
    'description': 'Create static type event',
    'long_description': '# strong-lambda\nAWS Lambda enhancements\n\nPython 3 introduced some very interesting things when it comes to static typing programming.\nThis package uses these new features in order to make AWS Lambda more static type driven.\n\n\n## External links\n1. [The benefits of static typing without static typing in Python](https://pawelmhm.github.io/python/static/typing/type/annotations/2016/01/23/typing-python3.html\n) \n1. [AWS Lambda](https://aws.amazon.com/lambda/)\n1. [typing Python — Support for type hints](https://docs.python.org/3/library/typing.html)\n',
    'author': 'Rodrigo Farias Rezino',
    'author_email': 'rodrigofrezino@gmail.com',
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
