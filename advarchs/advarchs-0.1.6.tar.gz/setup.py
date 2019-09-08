# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['advarchs']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.22,<3.0', 'tomlkit>=0.5.5,<0.6.0']

setup_kwargs = {
    'name': 'advarchs',
    'version': '0.1.6',
    'description': 'Data retrieval from remote archives',
    'long_description': 'Advarchs: Data retrieval from remote archives\n=============================================\n\n.. image:: https://img.shields.io/pypi/v/advarchs.svg\n   :target: https://pypi.python.org/pypi/advarchs\n   :alt: PyPI Version\n\n.. image:: https://img.shields.io/pypi/pyversions/advarchs.svg\n   :target: https://pypi.python.org/pypi/advarchs\n   :alt: Supported Python Versions\n\n.. image:: https://img.shields.io/travis/elessarelfstone/advarchs/master.svg\n   :target: https://travis-ci.org/elessarelfstone/advarchs\n   :alt: Build Status\n\n.. image:: https://img.shields.io/badge/wheel-yes-brightgreen.svg\n   :target: https://pypi.python.org/pypi/advarchs\n   :alt: Wheel Status\n\nOverview\n--------\nAdvarchs is simple tool for retrieving data from web archives.\nIt is especially useful if you are working with remote data stored in compressed\nspreadsheets or of similar format.\n\nGetting Started\n---------------\n\nSay you need to perform some data anlytics on an excel spreadsheet that gets\nrefreshed every month and stored in RAR format. You can target a that file\nand convert it to a pandas_ dataframe with the following procedure:\n\n.. code-block:: python\n\n    import pd\n    import os\n    import tempfile\n    from advarchs import webfilename,extract_web_archive\n\n    TEMP_DIR = tempfile.gettempdir()\n\n    url = "http://www.site.com/archive.rar"\n    arch_file_name = webfilename(url)\n    arch_path = os.path.join(TEMP_DIR, arch_file_name)\n    xlsx_files = extract_web_archive(url, arch_path, ffilter=[\'xlsx\'])\n    for xlsx_f in xlsx_files:\n        xlsx = pd.ExcelFile(xlspath)\n\n    ...\n\nRequirements\n------------\n\n- ``Python 3.5+``\n- ``p7zip``\n\nSpecial note\n~~~~~~~~~~~~\n\nOn CentOS and Ubuntu <= 16.04, the following packages are needed:\n\n- ``unrar``\n\nInstallation\n------------\n\n.. code-block:: shell\n\n    pip install advarchs\n\nContributing\n------------\nSee `CONTRIBUTING`_\n\nCode of Conduct\n~~~~~~~~~~~~~~~\nThis project adheres to the `Contributor Covenant 1.2`_.\nBy participating, you are advised to adhere to this Code of Conduct in all your\ninteractions with this project.\n\nLicense\n-------\n\n`Apache-2.0`_\n\n.. _`pandas`: https://pypi.org/project/pandas/\n.. _`CONTRIBUTING`: https://github.com/elessarelfstone/advarchs/blob/master/CONTRIBUTING.md\n.. _`Contributor Covenant 1.2`: http://contributor-covenant.org/version/1/2/0\n.. _`Apache-2.0`: https://github.com/elessarelfstone/advarchs/blob/master/LICENSE\n',
    'author': 'Dauren Sdykov',
    'author_email': 'elessarelfstone@mail.ru',
    'url': 'https://github.com/elessarelfstone/advarchs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
