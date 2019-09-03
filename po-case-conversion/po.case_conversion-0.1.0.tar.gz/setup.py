# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['po',
 'po.case_conversion',
 'po.case_conversion._vendor',
 'po.case_conversion._vendor.regex',
 'po.case_conversion._vendor.regex.test']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'po.case-conversion',
    'version': '0.1.0',
    'description': 'Convert between different types of cases (unicode supported)',
    'long_description': '### This is a fork\nAll credit goes to Alejandro Frias - [here is the original repo](github.com//AlejandroFrias/case-conversion).\nI only forked to gain vendorized dependencies.\n\n## Case Conversion\nThis is a port of the [CaseConversion Sublime Plugin](https://github.com/jdc0589/CaseConversion), by [Davis Clark\'s](https://github.com/jdc0589), to a regular python package. I couldn\'t find any other python packages on PyPi at the time (Feb 2016) that could seamlessly convert from any case to any other case without having to specify from what type of case I was converting. This plugin worked really well, so I separated the (non-sublime) python parts of the plugin into this useful python package. I also added Unicode support using the `regex` package. Credit goes to [Davis Clark\'s](https://github.com/jdc0589) and the contributors to that plugin (Scott Bessler, Curtis Gibby, Matt Morrison) for their awesome work on making such a robust and awesome case converter.\n\n#### Features\n\n- Autodetection of case (no need to specify explicitly which case you are converting from!)\n- Unicode supported (non-ASCII characters for days!)\n- Acronym detection (no funky splitting on every capital letter of an all caps acronym like `HTTPError`!)\n- And obviously case conversions from/to the following types of cases:\n  - `camelcase`\n  - `pascalcase`\n  - `snakecase`\n  - `dashcase`\n  - `spinalcase` (alias for `dashcase`)\n  - `kebabcase` (alias for `dashcase`)\n  - `constcase`\n  - `screaming_snakecase` (alias for `constcase`)\n  - `dotcase`\n  - `separate_words`\n  - `slashcase`\n  - `backslashcase`\n- Oh! Python2 and Python3 supported!\n\n\n##### Usage\n\nNormal use is self-explanatory.\n\n```python\n>>> import case_conversion\n>>> case_conversion.kebabcase("FOO_BAR_STRING")\n\'foo-bar-string\'\n>>> print(case_conversion.constcase(u"fóó-bar-string"))\nFÓÓ_BAR_STRING\n```\n\nTo use acronym detection set `detect_acronyms` to `True` and pass in a list of `acronyms` to detect as whole words.\n\n```python\n>>> import case_conversion\n>>> case_conversion.snakecase("fooBarHTTPError")\n\'foo_bar_h_t_t_p_error\'  # ewwww\n>>> case_conversion.snakecase("fooBarHTTPError", detect_acronyms=True, acronyms=[\'HTTP\'])\n\'foo_bar_http_error\'  # pretty\n```\n\n## Install\n\n```\npip install case-conversion\n```\n\n\n## Licence\n\nUsing [MIT licence](LICENSE.txt) with Davis Clark\'s Copyright\n',
    'author': 'Alejandro Frias',
    'author_email': 'joker454@gmail.com',
    'url': 'https://github.com/olsonpm/case-conversion',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
