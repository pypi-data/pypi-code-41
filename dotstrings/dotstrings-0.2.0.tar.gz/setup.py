# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dotstrings']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'dotstrings',
    'version': '0.2.0',
    'description': 'Tools for dealing with the .strings files for iOS and macOS',
    'long_description': '# dotstrings\n\nThis is a Python toolkit for interacting with the localization files for iOS and macOS.\n\n### Examples\n\n**Read in a .strings file and print the entries:**\n```python\nimport dotstrings\n\nentries = dotstrings.load("/path/to/file.strings")\n\nfor entry in entries:\n    print("Key: " + entry.key)\n    print("Value: " + entry.value)\n    print("Comment: " + entry.comment)\n```\n\n# Contributing\n\nThis project welcomes contributions and suggestions.  Most contributions require you to agree to a\nContributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us\nthe rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.\n\nWhen you submit a pull request, a CLA bot will automatically determine whether you need to provide\na CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions\nprovided by the bot. You will only need to do this once across all repos using our CLA.\n\nThis project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).\nFor more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or\ncontact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.\n',
    'author': 'Dale Myers',
    'author_email': 'dalemy@microsoft.com',
    'url': 'https://github.com/Microsoft/dotstrings',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
