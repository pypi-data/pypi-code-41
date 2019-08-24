# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['statmake']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=18.2', 'cattrs>=0.9', 'fonttools[ufo]>=3.38']

entry_points = \
{'console_scripts': ['statmake = statmake.cli:main']}

setup_kwargs = {
    'name': 'statmake',
    'version': '0.2.0',
    'description': 'Applies STAT information from a Stylespace to a variable font.',
    'long_description': "# statmake\n\n`statmake` takes a user-written Stylespace that defines [OpenType `STAT` information](https://docs.microsoft.com/en-us/typography/opentype/spec/stat) for an entire font family and then (potentially subsets and) applies it to a specific variable font. This spares users from having to deal with [raw TTX dumps](https://github.com/fonttools/fonttools/) and juggling with nameIDs.\n\n## Installation\n\nThe easiest way is by installing it with `pip`. You need at least Python 3.6.\n\n```\npip3 install statmake\n```\n\n## Usage\n\n\n### External Stylespace file, stand-alone or referenced from a Designspace file\n\nIf you are producing more than one variable font (i.e. you have multiple Designspace files), you can avoid duplicated information by writing a single all-encompassing Stylespace file which statmake will subset for each variable font.\n\n**Attention:** A `STAT` table is supposed to describe a font's relationship to the _entire_ family. If you have separate upright and italic variable fonts with a `wght` axis each, you need to mark each font's position on the `ital` axis _in the Designspace lib `org.statmake.additionalLocations` key_. The Designspace `<axes>` elements are not supposed to hold this information, so it must be done in a separate lib key.\n\n1. Write a Stylespace file that describes each stop of all axes available in the entire family. See [tests/data/Test.stylespace](tests/data/Test.stylespace) for an annotated example. You can also use it as a starting point.\n2. You can have the file stand-alone or use the Designspace lib's `org.statmake.stylespacePath` key to store the path to the Stylespace file relative to the Designspace file. See [tests/data/TestExternalStylespace.designspace](tests/data/TestExternalStylespace.designspace) for an example.\n3. If you have one or more Designspace files which do not define all axes available to the family, you have to annotate them with the missing axis locations to get a complete `STAT` table. See the lib key at the bottom of [tests/data/Test_Wght_Upright.designspace](tests/data/Test_Wght_Upright.designspace) and [tests/data/Test_Wght_Italic.designspace](tests/data/Test_Wght_Italic.designspace) for an example.\n4. Generate the variable font(s) as normal\n5. If...\n    1. ... you store the Stylespace file stand-alone: run `statmake --designspace variable_font.designspace --stylespace your.stylespace variable_font.ttf`.\n    2. ... you store the Stylespace inline in the Designspace file or as a stand-alone file and added the relative path to it in the Designspace's `org.statmake.stylespacePath` key: run `statmake --designspace variable_font.designspace variable_font.ttf`\n\nBe sure to use the Designspace file that was used to generate the font to get the correct missing axis location definitions.\n\n### Designspace file with inline Stylespace data\n\nIf you are producing a single variable font containing an entire family, this approach will save you an external file.\n\n1. Write the file as above, point 1.\n2. Insert it into the Designspace file's lib under the `org.statmake.stylespace` key. See [tests/data/TestInlineStylespace.designspace](tests/data/TestInlineStylespace.designspace) for an example.\n3. Proceed from point 3 above.\n\n## Q: Can I please have something other than a .plist file?\n\nYes, but you have to convert it to `.plist` yourself, as statmake currently only read `.plist` files. One possible converter is Adam Twardoch's [yaplon](https://pypi.org/project/yaplon/).\n",
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
