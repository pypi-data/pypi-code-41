# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['kagi',
 'kagi.management',
 'kagi.management.commands',
 'kagi.migrations',
 'kagi.tests',
 'kagi.views']

package_data = \
{'': ['*'], 'kagi': ['static/kagi/*', 'templates/kagi/*']}

install_requires = \
['Django>=2.2,<3.0', 'qrcode>=6.1,<7.0', 'webauthn>=0.4.5,<0.5.0']

setup_kwargs = {
    'name': 'kagi',
    'version': '0.1.0',
    'description': 'Django app for WebAuthn and TOTP-based multi-factor authentication',
    'long_description': 'Kagi\n----\n\n.. image:: https://circleci.com/gh/justinmayer/kagi.svg?style=svg\n    :target: https://circleci.com/gh/justinmayer/kagi\n\nKagi provides support for FIDO WebAuthn security keys and TOTP tokens in Django.\n\nKagi is a working proof-of-concept and isn\'t yet production ready. There are\nmany TODOs sprinkled around the code that should be fixed before relying on it.\n\nInstallation\n============\n\n::\n\n    $ pip install kagi\n\nAdd ``kagi`` to ``INSTALLED_APPS`` and include ``kagi.urls`` somewhere in your\nURL patterns. Set ``LOGIN_URL = \'kagi:login\'``.\n\nMake sure that Django\'s built-in login view does not have a\n``urlpattern``, because it will authenticate users without their second\nfactor. Kagi provides its own login view to handle that.\n\nDemo\n====\n\nTo see a demo, use the test project included in the repo and perform the\nfollowing steps (using a virtual environment is optional)::\n\n   git clone https://github.com/justinmayer/kagi\n   cd kagi\n   make install\n   make serve\n\n   cd testproj\n   python manage.py migrate\n   python manage.py createsuperuser\n\nSupported browsers and versions can be found here: https://caniuse.com/webauthn\nWebAuthn also requires that the site is served over a secure (HTTPS) connection.\n\nStart by going to https://localhost:8000/kagi/login. Since you\nhaven\'t added any security keys yet, you will be logged in with just a\nusername and password.\n\nOnce logged in, click "Add another key" on the key management page and follow\nthe instructions. Now your account is protected by multi-factor authentication,\nand when you log in again your WebAuthn key or TOTP token will be required.\n\nYou can manage the keys attached to your account on the key\nmanagement page as well, at the URL https://localhost:8000/kagi/keys.\n\n\nUsing WebAuthn Keys on Linux\n============================\n\nSome distros don\'t come with udev rules to make USB HID /dev/\nnodes accessible to normal users. If your key doesn\'t light up\nand start flashing when you expect it to, this might be what is\nhappening. See https://github.com/Yubico/libu2f-host/issues/2 and\nhttps://github.com/Yubico/libu2f-host/blob/master/70-u2f.rules for some\ndiscussion of the rule to make it accessible. If you just want a quick\ntemporary fix, you can run ``sudo chmod 666 /dev/hidraw*`` every time\nafter you plug in your key (the files disappear after unplugging).\n',
    'author': 'Justin Mayer',
    'author_email': 'entroP@gmail.com',
    'url': 'https://github.com/justinmayer/kagi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
