# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['whippet']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['whippet = whippet:console.main']}

setup_kwargs = {
    'name': 'whippet',
    'version': '0.2.3',
    'description': 'Install make based hooks with ease.',
    'long_description': 'Whippet - like husky, but leaner\n################################\nA simple git hooks installer. Inspired by `husky <https://github.com/typicode/husky#readme>`_.\n\nI liked simplicity of setting up git hooks using husky and since I failed to find a similar tool in python ecosystem, I\ndecided to write one myself.\n\nAs far as I know there is no standard equivalent to `npm scripts <https://docs.npmjs.com/misc/scripts>`_ in python, so I\nchose to rely on `make <https://www.gnu.org/software/make/>`_ which seems to be a popular way to organise project\nrelated tasks in python world.\n\nInstall\n*******\nWhippet is available as a `pypi package <https://pypi.org/project/whippet/>`_. Use a tool that can install packages from\nit, like for instance `pip <https://pip.pypa.io/en/stable/>`_.\n\n.. code-block:: bash\n\n    $ pip install requests\n\nUsage\n*****\nOnce whippet is installed, it is used by invoking ``whippet`` executable in the directory where you wish to install\nhooks. Whippet will check if that directory (or its ancestor) contains a ``.git`` directory and offer to install hooks\ninto it.\n\n.. code-block:: bash\n\n    $ cd demo\n    $ whippet\n    whippet - Are you sure you want to install hooks in /home/bpp/demo/.git? [Y/n] y\n\nWhippet hooks are scripts that check for existence of make targets with the same name as git hooks. If such a target\nexists, script will execute it. Let\'s take ``pre-commit`` as an example. Once whippet hooks are installed, we simply add\n``pre-commit`` target to the Makefile like so:\n\n.. code-block:: make\n\n    pre-commit:\n        @echo "Hello from whippet"\n\n\nThen o\n',
    'author': 'Dalibor Novak',
    'author_email': 'BorePlusPlus@gmail.com',
    'url': 'https://github.com/BorePlusPlus/whippet',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
