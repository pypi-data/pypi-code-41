# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pwdmanager']

package_data = \
{'': ['*']}

install_requires = \
['python-gnupg>=0.4.5,<0.5.0']

entry_points = \
{'console_scripts': ['pwdmanager = pwdmanager.pwdmanager:main']}

setup_kwargs = {
    'name': 'pwdmanager',
    'version': '1.0.0',
    'description': 'command line tool to manage passwords',
    'long_description': "==========\npwdmanager\n==========\n\nKeep your passwords safe and close\n\nThis is a command line tool to manage your passwords. Those are stored locally in an encrypted JSON formatted file. The\nencryption and decryption is performed by GPG_. Passwords unlocking is done using a master password.\n\nBenefits of using this program include :\n\n- use difficult and different passwords to secure your accounts\n- you don't have to trust third parties for storing your passwords : everything is stored locally\n- provide high end and reliable encryption with GPG_\n- it is open source : anybody can check the code\n\ninstallation\n------------\n\nWith pip or your favorite package manager::\n\n    pip install pwdmanager\n    pipenv install pwdmanager\n    poetry add pwdmanager\n\nThat's it.\n\nIf you want to build the wheel yourself you have to have `poetry <https://poetry.eustace.io/>`_\ninstalled. Then change directory to the root of the sources and issue::\n\n    poetry build\n\nThen you can install the wheel with your favorite package manager::\n\n    pip install dist/pwdmanager-XXX-py3-none-any.whl\n    pipenv install dist/pwdmanager-XXX-py3-none-any.whl\n    poetry add pwdmanager --path=dist/pwdmanager-XXX-py3-none-any.whl\n\nrequirements\n------------\n\nYou need to have GPG_ installed.\n\n.. _GPG: https://gnupg.org/\n\ndatabase\n--------\n\nThe database is a local JSON file. It is encrypted. At first usage it will be initialised. The default location is\n``~/.pwddb`` but you can provide you own location.\n\nconcepts\n--------\n\nAn entry in basically a container for an account information. The password database is a list of entries. An entry has\nthe following attributes:\n\nname\n    this is an id of the entry. Two entries cannot have the same name.\n\nlogin\n    account login\n\npassword\n    account password\n\nlogin alias\n    a second or alternative account login\n\naliases\n    one entry can have several aliases. Each alias is an id of the entry. Two entries cannot have the same alias.\n    Useful to provide easier to match or remember names\n\ntags\n    one entry can have several tags. Useful to categorize entries. You can search with tags\n\ncreation date\n    entry creation date. Immutable.\n\nlast update date\n    obvious\n\nusage\n-----\n::\n\n    usage: pwdmanager [-h] [-d DATABASE] [-p MASTER_PASSWORD]\n                        {add,show,list,rm,update} ...\n\n    positional arguments:\n      {add,show,list,rm,update}\n\n    optional arguments:\n      -h, --help            show this help message and exit\n      -d DATABASE, --database DATABASE\n                            specify where the database is located\n      -p MASTER_PASSWORD, --master-password MASTER_PASSWORD\n                            password to crypt and decrypt the database\n\n\nThere are 5 main commands:\n\nadd\n    to add a new entry\n\nshow\n    to list all the attributes of a particular entry, you have to give the exact name or alias of an entry\n\nlist\n    to look for entries. Can be used without any parameter, in that case all entries will be listed. You can also provide\n    a string, then all the entries with name or aliases containing this string will be listed. You can filter by tag also.\n\nrm\n    to remove an entry. No confirmation asked, be careful.\n\nupdate\n    to modify an entry\n\nFor all those commands, use the ``-h/--help`` flag to have details about parameters::\n\n    pwdmanager add -h\n\n\nbe careful\n----------\n\n- Choose your master password wisely. Do not forget it or you won't be able to recover your database\n- When adding a password you specify it in the command. Thus it may be stored in the shell history. Therefore I strongly\n  recommend to clean your history after adding passwords. On linux ``sed -i /^pwdmanager/d ~/.bash_history`` will do the trick\n  in most cases.\n- When adding a password I recommend you surround it by single quotes because special characters may be interpreted\n  by the shell\n- back your password database up\n",
    'author': 'Alexandre G',
    'author_email': 'alex.git@ralouf.fr',
    'url': 'https://github.com/bravefencermusashi/pwdmanager',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
