# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['localizationkit', 'localizationkit.tests']

package_data = \
{'': ['*']}

install_requires = \
['toml==0.10.0']

setup_kwargs = {
    'name': 'localizationkit',
    'version': '0.4.0',
    'description': 'String localization tests',
    'long_description': '# localizationkit\n\n`localizationkit` is a toolkit for ensuring that your localized strings are the best that they can be.\n\nIncluded are tests for various things such as:\n\n* Checking that all strings have comments\n* Checking that the comments don\'t just match the value\n* Check that tokens have position specifiers\n* Check that no invalid tokens are included\n\nwith lots more to come. \n\n## Getting started\n\n### Configuration\n\nTo use the library, first off, create a configuration file that is in the TOML format. Here\'s an example:\n\n```toml\ndefault_language = "en"\n\n[has_comments]\nminimum_comment_length = 25\nminimum_comment_words = 8\n\n[token_matching]\nallow_missing_defaults = true\n\n[token_position_identifiers]\nalways = false\n```\n\nThis configuration file sets that `en` is the default language (so this is the language that will be checked for comments, etc. and all tests will run relative to it). Then it sets various settings for each test. Every instance of `[something_here]` specifies that the following settings are for that test. For example, the test `has_comments` will now make sure that not only are there comments, but that they are at least 25 characters in length and 8 words in length. \n\nYou can now load in your configuration:\n\n```python\nfrom localizationkit import Configuration\n\nconfiguration = Configuration.from_file("/path/to/config.toml")\n```\n\n### Localization Collections\n\nNow we need to prepare the strings that will go in. Here\'s how you can create an individual string:\n\n```python\nfrom localizationkit import LocalizedString\n\nmy_string = LocalizedString("My string\'s key", "My string\'s value", "My strings comment", "en")\n```\n\nThis creates a single string with a key, value and comment, with its language code set to `en`. Once you\'ve created some more (usually for different languages too), you can bundle them into a collection:\n\n```python\nfrom localizationkit import LocalizedCollection\n\ncollection = LocalizedCollection(list_of_my_strings)\n```\n\n### Running the tests\n\nAt this point, you are ready to run the tests:\n\n```python\nimport localizationkit\n\nresults = localizationkit.run_tests(configuration, collection)\n\nfor result in results:\n    if not result.succeeded():\n        print("The following test failed:", result.name)\n        print("Failures encountered:")\n        for violation in result.violations:\n            print(violation)\n```\n\n### Not running the tests\n\nSome tests don\'t make sense for everyone. To skip a test you can add the following to your config file at the root:\n\n```toml\nblacklist = ["test_identifier_1", "test_identifier_2"]\n```\n\n# Contributing\n\nThis project welcomes contributions and suggestions.  Most contributions require you to agree to a\nContributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us\nthe rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.\n\nWhen you submit a pull request, a CLA bot will automatically determine whether you need to provide\na CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions\nprovided by the bot. You will only need to do this once across all repos using our CLA.\n\nThis project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).\nFor more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or\ncontact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.\n',
    'author': 'Dale Myers',
    'author_email': 'dalemy@microsoft.com',
    'url': 'https://github.com/Microsoft/localizationkit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
