# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['centrifuge_cli']

package_data = \
{'': ['*']}

install_requires = \
['Click>=7.0,<8.0', 'pandas>=0.25.1,<0.26.0', 'requests>=2.22,<3.0']

entry_points = \
{'console_scripts': ['centrifuge = centrifuge_cli.main:cli']}

setup_kwargs = {
    'name': 'centrifuge-cli',
    'version': '0.1.1',
    'description': "A command line utility for interacting with the Centrifuge Firmware Analysis Platform's REST API.",
    'long_description': 'centrifuge-cli: The official Python library and CLI for Centrifuge\n==================================================================\n\nCentrifuge is an automated firmware analysis platform. It allows users to upload\ntheir firmware images to be analyzed for various security issues. This utility\ngives users the ability to interact and automate tasks via the Centrifuge\nRESTful API.\n\nFeatures\n--------\n\n- Upload firmware\n- Delete firmware reports\n- Query firmware analysis results\n- Search for firmware uploads\n\nQuick Start\n-----------\n\n\nTo install the Centrifuge CLI, simply:\n\n.. code-block:: bash\n\n    $ pip install centrifuge-cli\n\nTo query the list of available reports:\n\n.. code-block:: bash\n\n    $ export CENTRIFUGE_API_KEY=xxxx\n    $ centrifuge reports list\n\nUnder the hood the Centrifuge CLI is using python Pandas data frames to report\nthe results to the user. Since the API is json, which has heirarchical structure\nto it, we have chosen to flatten all the results into a column/row format for\nviewing inside of a terminal or for importing into spreadsheets, etc. However\nthe cli can also output CSV, and the original json results. For example:\n\nCSV:\n\n.. code-block:: bash\n\n    $ centrifuge --outfmt=csv reports list\n\nJSON:\n\n.. code-block:: bash\n\n    $ centrifuge --outfmt=json reports list\n\nWhen generating the human-readable Pandas output or when genering CSV you have\nthe option of choosing which columns you wish to export. For example, to display\nonly the original filename and model number of the firmware that was uploaded: \n\n.. code-block:: bash\n\n    $ centrifuge -foriginalFilename -fdevice reports list\n\n\nUploading Firmware\n------------------\nUploading firmware to centrifuge is quite simple. All you need to do is supply\nmake/model/version and the file you want to upload:\n\n.. code-block:: bash\n\n    $ centrifuge upload --make=Linksys --model=E1200 --version=1.0.04 /path/to/FW_E1200_v1.0.04.001_US_20120307.bin\n\nSearching Through Firmware Uploads\n----------------------------------\n\nComing Soon\n\nQuerying Report Results\n------------------------\n\nComing Soon\n\nDeleting Firmware Uploads\n-------------------------\n\nComing Soon\n',
    'author': 'Peter Eacmen',
    'author_email': 'peacmen@refirmlabs.com',
    'url': 'https://www.refirmlabs.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
