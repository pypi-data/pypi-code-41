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
    'version': '0.2.4',
    'description': 'Install make based hooks with ease.',
    'long_description': 'Whippet - like husky, but leaner\n################################\nUse `make <https://www.gnu.org/software/make/>`_ targets to execute git hooks. Inspired by `husky <https://github.com/typicode/husky#readme>`_.\n\nRationale\n*********\nI liked the simplicity of setting up git hooks using husky, and since I failed to find a similar tool in python ecosystem, I decided to write one myself.\n\nAs far as I know, there is no standard equivalent to `npm scripts <https://docs.npmjs.com/misc/scripts>`_ in python, so I chose to rely on make which seems to be a popular way to organise project-related tasks in the python world.\n\nInstallation\n************\nWhippet is available as a `PyPI package <https://pypi.org/project/whippet/>`_. Use a tool that can install packages from it, like for instance `pip <https://pip.pypa.io/en/stable/>`_.\n\n.. code-block:: bash\n\n    $ pip install whippet\n\nUsage\n*****\n\nInstall hooks\n-------------\nOnce whippet is installed, it is used by invoking ``whippet`` executable in the directory where you wish to install hooks. Whippet checks if that directory (or its ancestor) contains a ``.git`` directory and offer to install hooks into it.\n\n.. code-block:: bash\n\n    $ cd demo\n    $ whippet\n    whippet - Are you sure you want to install hooks in /home/bpp/demo/.git? [Y/n] y\n\nSetup target\n------------\nWhippet hooks are scripts that check for the existence of make targets with the same name as git hooks. If such a target exists, the script executes it. Let\'s take ``pre-commit`` as an example. Once whippet hooks are installed, we simply add ``pre-commit`` target to the Makefile like so:\n\n.. code-block:: make\n\n    pre-commit:\n        @echo "Whippet says: Woof!"\n\n\nThen the target will be executed on ``pre-commit``:\n\n.. code-block:: bash\n\n    $ git ci -m \'Testing whippet\'\n    pre-commit\n    Whippet says: Woof!\n    [master d654d33] Bar\n    1 file changed, 12 insertions(+)\n    create mode 100644 Makefile\n    $\n\n\nNon-interactive\n---------------\nTo avoid the prompt pass the ``--assume-yes`` argument to whippet. This can be useful when adding whippet to initialisation target in Makefile. Example:\n\n.. code-block:: make\n\n    init:\n        poetry install\n        whippet --assume-yes\n\n\n',
    'author': 'Dalibor Novak',
    'author_email': 'BorePlusPlus@gmail.com',
    'url': 'https://github.com/BorePlusPlus/whippet',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
