# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['statmake']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=18.2', 'cattrs>=0.9.0,<0.10.0', 'fonttools[ufo]>=3.38,<4.0']

entry_points = \
{'console_scripts': ['statmake = statmake.cli:main']}

setup_kwargs = {
    'name': 'statmake',
    'version': '0.1.3',
    'description': 'Applies STAT information from a Stylespace to a variable font.',
    'long_description': "# statmake\n\n`statmake` takes a user-written Stylespace that defines [OpenType `STAT` information](https://docs.microsoft.com/en-us/typography/opentype/spec/stat) for an entire font family and then (potentially subsets and) applies it to a specific variable font. This spares users from having to deal with [raw TTX dumps](https://github.com/fonttools/fonttools/) and juggling with nameIDs.\n\n## Installation\n\nThe easiest way is by installing it with `pip`. You need at least Python 3.6.\n\n```\npip3 install statmake\n```\n\n## Usage\n\n1. Write a Stylespace file that describes each stop of all axes available in the entire family. See [tests/data/Test.stylespace](tests/data/Test.stylespace) for an annotated example.\n2. If you have one or more Designspace files which do not define all axes available to the family, you have to annotate them with the missing axis locations to get a complete `STAT` table. See the lib key at the bottom of [tests/data/Test_Wght_Upright.designspace](tests/data/Test_Wght_Upright.designspace) and [tests/data/Test_Wght_Italic.designspace](tests/data/Test_Wght_Italic.designspace) for an example.\n3. Generate the variable font(s) as normal\n4. Run `statmake your.stylespace variable_font.designspace variable_font.ttf`. Take care to use the Designspace file that was used to generate the font to get the correct missing axis location definitions.\n\n### Q: Can I please have something other than a .plist file?\n\nYes, but you have to convert it to `.plist` yourself, as statmake currently only read `.plist` files. One possible converter is Adam Twardoch's [yaplon](https://pypi.org/project/yaplon/).\n",
    'author': 'Nikolaus Waxweiler',
    'author_email': 'nikolaus.waxweiler@daltonmaag.com',
    'url': 'https://github.com/daltonmaag/statmake',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
