# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['slcp']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['slcp = slcp.__main__:main']}

setup_kwargs = {
    'name': 'slcp',
    'version': '0.3.0',
    'description': 'Copy all files with given extensions from a directory and its subfolders to another directory.',
    'long_description': "# Selective Copy v0.3.0\n[![Python Version](https://img.shields.io/pypi/pyversions/slcp.svg)](https://www.python.org/downloads/release/python-370/)\n[![PyPi Version](https://img.shields.io/pypi/v/slcp.svg)](https://pypi.org/project/slcp/)\n[![Codacy Badge](https://api.codacy.com/project/badge/Grade/bdde9d33956642129d82d219328ad5cc)](https://www.codacy.com/app/pltnk/selective_copy?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=pltnk/selective_copy&amp;utm_campaign=Badge_Grade)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![License](https://img.shields.io/github/license/pltnk/selective_copy.svg)](https://choosealicense.com/licenses/mit/)\n\nSimple command line application that copies all files with given extensions from a directory and its subfolders to another directory showing progress bar and remaining files counter.\\\nAllows to preserve a source folder structure, to process only files without given extensions, to move files instead of copying, to exclude certain files from processing and to create a log if necessary.\\\nOpens a filedialog if source and/or destination are not given in the command line.\\\nCreates folders in a destination path if they don't exist.\n\n## Installing\n\n```pip install slcp```\n\n## Usage\n\n<pre>\nslcp ext [ext ...] [-s SRC] [-d DST] [-sc | -dc] [-p] [-i] [-m] [-e FILE [FILE ...]] [-l] [-h]\n\nPositional arguments:\next                         One or more extensions of the files to copy. \n                            Enter extensions without a dot and separate by spaces.\n\nOptional arguments:\n-s SRC, --source SRC        Source folder path.\n-d DST, --dest DST          Destination folder path.\n-sc, --srccwd               Use current working directory as a source folder.\n-dc, --dstcwd               Use current working directory as a destination folder.\n-p, --preserve              Preserve source folder structure.\n-i, --invert                Process only files without given extensions.\n-m, --move                  Move files instead of copying, be careful with this option.\n-e FILE [FILE ...],         Exclude one or more files from processing.\n--exclude FILE [FILE ...]   Enter filenames with extensions and separate by spaces.\n-l, --log                   Create and save log to the destination folder.\n-h, --help                  Show this help message and exit.\n</pre>\n\n### Examples\n\n[![asciicast](https://asciinema.org/a/263359.svg)](https://asciinema.org/a/263359?t=2)\n\n## Changelog\n\n### [v0.3.0](https://github.com/pltnk/selective_copy/releases/tag/v0.3.0) - 2019-08-22 \n#### Added\n- [Black](https://github.com/psf/black) code style\n\n#### Changed\n- The code is now divided into separate modules\n- Dots that come with extensions are removed from output folder name. \nThe reason is that folders with a name starting with a dot are considered as hidden on Linux.\n- Log saving indication\n- Name of the logfile\n\n#### Fixed\n- Issue when paths like /home/user/test and /home/user/test2 were considered as nested which lead to an error.\n\n[Compare with v0.2.1](https://github.com/pltnk/selective_copy/compare/v0.2.1...v0.3.0)\n\n### [v0.2.1](https://github.com/pltnk/selective_copy/releases/tag/v0.2.1) - 2019-07-16 \n#### Added\n- Changelog\n\n#### Fixed\n- Readme of the project on [PyPI](https://pypi.org/project/slcp/) and [GitHub](https://github.com/pltnk/selective_copy)\n\n[Compare with v0.2.0](https://github.com/pltnk/selective_copy/compare/v0.2.0...v0.2.1)\n\n### [v0.2.0](https://github.com/pltnk/selective_copy/releases/tag/v0.2.0) - 2019-07-15 \n#### Added\n- Support of processing several extensions at once\n- --invert option\n- --move option\n- --exclude option\n\n[Compare with v0.1.0](https://github.com/pltnk/selective_copy/compare/v0.1.0...v0.2.0)\n\n## License\n\nThis project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details\n\n## Acknowledgments\n\nInspired by the task from [Chapter 9 of Automate the Boring Stuff](https://automatetheboringstuff.com/chapter9/).\n",
    'author': 'Kirill Plotnikov',
    'author_email': 'init@pltnk.dev',
    'url': 'https://github.com/pltnk/selective_copy',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
