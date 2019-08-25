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
 'delegator.py>=0.1.1,<0.2.0',
 'python-dotenv>=0.10.3,<0.11.0',
 'toml>=0.10.0,<0.11.0']

entry_points = \
{'console_scripts': ['dj = dj:__main__.run']}

setup_kwargs = {
    'name': 'dj-command',
    'version': '0.5.2',
    'description': 'Run commands with `dj {command_name}`. Uses aliases defined in a simple config file or defaults to Django management commands.',
    'long_description': '# Why?\nIt is available everywhere if you install via `pip`, has cute aliases defined in a JSON file (`.dj-config.json`) per project, will run as many commands as you want, and defaults to Django management commands if an alias cannot be found.\n\nCommands can be run sequentially by `dj` (e.g. `dj makemigrations migrate`). However, calling a long-running process (e.g. `dj runserver`) will prevent any other commands from being run. For example, `dj runserver migrate` will never run the `migrate` command because `runserver` will block the process.\n\n# Configuration file\n\n## Example .dj-config.toml\n```toml\ndisable_django_management_command = false\npython_interpreter = "python"\nenvironment_file_path = ".env"\n\n[[commands]]\nname = "m"\nhelp = "Does the migration dance"\nexecute = "./manage.py makemigrations && ./manage.py migrate"\nrequires_virtualenv = true\n\n[[commands]]\nname = "r"\nhelp = "Runs all the servers"\nexecute = "./manage.py runserver"\nrequires_virtualenv = true\nlong_running = true\n\n[[commands]]\nname = "ls"\nhelp = "Lists all the files, of course"\nexecute = "ls"\n\n[[commands]]\nname = "up"\nhelp = "Up all the things"\nexecute = "pip3 install -r requirements/development.txt && ./manage.py migrate && ./manage.py runserver"\nrequires_virtualenv = true\nlong_running = true\n\n[[commands]]\nname = "restore_database"\nhelp = "Restores a Postgres database from live to local"\nexecute = "PGPASSWORD=$PGPASSWORD pg_dump $DATABASE_NAME --host=$DATABASE_HOST --port=$DATABASE_PORT --username=$DATABASE_USERNAME --format=tar | pg_restore --clean --dbname=$DATABASE_NAME --no-owner --host=localhost --port=5432"\n```\n\n## Config file location\nIf the `--config` argument is used to specify a particular file location, that is the only place `dj` looks for a configuration file.\n\nOtherwise, `dj` will search for appropriate config files and "merge" them together. This allows you to have a base config file in `~/.dj-config.toml`, but override it on a per-folder basis. `dj` prioritizes `.toml` config files over `.json`. So, it will look for `~/.dj-config.toml` first and, if it\'s missing, then look for `~/.dj-config.json`. Then, it will follow the same pattern for the current directory. The current directory\'s config file will take precedence if there is an overlap in configuration settings.\n\n## Using environment variables in commands\n`dj` will look for a `.env` file to load environment variables using the wonderful [python-dotenv](https://github.com/theskumar/python-dotenv) library. You can specify environment variables in an execute command just like you would from the shell (i.e. `$VARIABLE_NAME`).\n\n# Basic arguments and options\n- `dj --help` to see all of the options\n- `dj --list` to see all of the available custom commands\n- `dj {command_name}` to run a custom command or Django management command (e.g. `dj migrate`)\n- `dj {command_name} {command_name} {command_name}` to run multiple commands (e.g. `dj makemigrations migrate`)\n- `dj {command_name} --dry_run` to show what commands would run without actually executing them\n\n# How to work on the source\n1. Clone the repo\n1. Run the source locally: `poetry run python dj`\n1. Test the source: `poetry run pytest`\n1. Build and install locally: `poetry build && pip3 install --user --force-reinstall .`\n1. Test with `~/.local/bin/dj migrate`\n1. Publish the source to pypi: `poetry publish --build --username USERNAME --password PASSWORD`\n\n# Acknowledgements\n- [poetry](https://poetry.eustace.io/): please, please, please continue to help wrangle the complexity of 1) creating Python projects, and 2) installing dependencies; seriously, it\'s baffling out there without you\n- [click](https://click.palletsprojects.com/): ridiculously full-featured library to help implement CLI programs in Python; it has all the bells and most of the whistles\n- [attrs](https://www.attrs.org/): would you like easy classes in Python? yes, please\n- [delegator.py](https://github.com/amitt001/delegator.py): `subprocess` is a pain, but `delegator` hides all the ugly cruft behind a nice API\n- [python-dotenv](https://github.com/theskumar/python-dotenv): 12-factor all the things with .env files\n- [toml](https://github.com/uiri/toml): the fewer braces in my life the better\n\n# Prior art\nThis isn\'t a new idea and there are a few other implementations out there that do similar things. But, uh, I like mine. 😀\n- [dj-cmd](https://pypi.org/project/dj-cmd/)\n- [Django-dj](https://github.com/h4l/Django-dj)\n- [dj-cli](https://pypi.org/project/dj-cli/)\n',
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
