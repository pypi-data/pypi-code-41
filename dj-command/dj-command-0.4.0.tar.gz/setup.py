# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dj']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.1,<20.0',
 'click>=7.0,<8.0',
 'colorama>=0.4.1,<0.5.0',
 'delegator.py>=0.1.1,<0.2.0']

entry_points = \
{'console_scripts': ['dj = dj:__main__.run']}

setup_kwargs = {
    'name': 'dj-command',
    'version': '0.4.0',
    'description': 'Run commands with `dj {command_name}`. Uses aliases defined in a simple config file or defaults to Django management commands.',
    'long_description': '# Why?\nIt is available everywhere if you install via `pip`, has cute aliases defined in a JSON file (`.dj-config.json`) per project, will run as many commands as you want, and defaults to Django management commands if an alias cannot be found.\n\nCommands can be run sequentially by `dj` (e.g. `dj makemigrations migrate`). However, calling a long-running process (e.g. `dj runserver`) will prevent any other commands from being run. For example, `dj runserver migrate` will never run the `migrate` command because `runserver` will block the process.\n\n# Example .dj-config.json\n```\n{\n\t"commands": [\n\t\t{\n\t\t\t"name": "nice name for the command",\n\t\t\t"help": "help text for the command (optional)",  \n\t\t\t"execute": "shell command to run",\n\t\t\t"long_running": false  // whether the process is expected to execute and exit or run forever (optional, defaults to false)\n\t\t\t"requires_virtualenv": false  // check that a virtual environment is activated before running the command (optional, defaults to false)\n\t\t},\n\t\t{\n\t\t\t"name": "m",\n\t\t\t"help": "Does the migration dance",\n\t\t\t"execute": "./manage.py makemigrations && ./manage.py migrate",\n\t\t},\n\t\t{\n\t\t\t"name": "r",\n\t\t\t"help": "Runserver",\n\t\t\t"execute": "./manage.py runserver",\n\t\t\t"long_running": true\n\t\t}\n\t],\n\t"disable_django_management_command": false  // prevent falling back to a Django management command cannot be found (optional, defaults to false)\n}\n```\n\n`dj` will look in the current directory for `.dj-config.json` and then in `~/`, unless the `--config` argument is used to specify a particular file location.\n\n# Basic arguments and options\n- `dj --help` to see all of the options\n- `dj --list` to see all of the available custom commands\n- `dj {command_name}` to run a custom command or Django management command (e.g. `dj migrate`)\n- `dj {command_name} --dry_run` to show what commands would run without actually executing them\n\n# How to work on the source\n1. Clone the repo\n1. Run the source locally: `poetry run python dj`\n1. Test the source: `poetry run pytest`\n1. Build and install locally: `poetry build && pip3 install --user --upgrade --force-reinstall dist/dj_command-0.3.0-py3-none-any.whl`\n1. Test with `~/.local/bin/dj migrate`\n1. Publish the source to pypi: `poetry publish --build --username USERNAME --password PASSWORD`\n\n# Acknowledgements\n- [poetry](https://poetry.eustace.io/): please, please, please continue to wrangle the complexity of 1) creating Python projects, and 2) installing dependencies; seriously, it\'s baffling out there without you\n- [click](https://click.palletsprojects.com/): ridiculously full-featured library to help implement CLI programs in Python; it has all the bells and most of the whistles\n- [attrs](https://www.attrs.org/): would you like easy classes in Python? yes, please\n- [delegator.py](https://github.com/amitt001/delegator.py): dealing with subprocess is a pain, but delegator hides all the ugly cruft behind a nice API\n\n# Prior art\nThis isn\'t a new idea and there are a few other implementations out there that do similar things. But, uh, I like mine. 😀\n- [dj-cmd](https://pypi.org/project/dj-cmd/)\n- [Django-dj](https://github.com/h4l/Django-dj)\n- [dj-cli](https://pypi.org/project/dj-cli/)\n',
    'author': 'Adam Hill',
    'author_email': 'adamghill@yahoo.com',
    'url': 'https://github.com/adamghill/dj',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
