# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['airduct', 'airduct.api', 'airduct.cli']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0',
 'crontab>=0.22.6,<0.23.0',
 'flask>=1.1,<2.0',
 'flask_cors>=3.0,<4.0',
 'psycopg2>=2.8,<3.0',
 'pyyaml>=5.1,<6.0',
 'sqlalchemy>=1.3,<2.0']

entry_points = \
{'console_scripts': ['airduct = airduct.cli.run:cli']}

setup_kwargs = {
    'name': 'airduct',
    'version': '0.1.9',
    'description': 'Simple Pipeline Scheduler in Python',
    'long_description': '# airduct\nSimple Pipeline Scheduler in Python\n\n![Airduct Screenshot](docs/screenshot.png)\n\n## Links\n\n- [Github](https://github.com/alairock/airduct)\n- [Documentation](https://airduct.readthedocs.io)\n\n## Installing\n    $ pip install airduct\n\nor\n\n    $ poetry add airduct\n\n## Quickstart\nAirduct calls pipelines "flows". A flow is a python file with a very particular definition, which is hopefully self explanatory.\n\nHere is an example flow:\n\n```python\nfrom airduct import schedule, task\n\n\nschedule(\n    name=\'ExampleFlow\',\n    run_at=\'* * * * *\',\n    flow=[\n        task(\'e1f1\'),\n        [task(\'e1f2\'), task(\'e1f3\', can_fail=True)],\n        [task(\'e1f4\')]\n    ]\n)\n\nasync def e1f1():\n    print(\'e1f1 - An async function!\')\n\ndef e1f2():\n    print(\'e1f2 - Regular functions work too\')\n\nasync def e1f3():\n    print(\'e1f3\')\n\nasync def e1f4():\n    print(\'e1f4\')\n```\n\nA flow requires a `airduct.scheduling.schedule` which runs at scheduler initialization. \nThe schedule function requires:\n - `name`: A name to identify the flow as, must be unique\n - `run_at`: A crontab-like scheduling syntax. (Uses this [crontab parser](https://github.com/josiahcarlson/parse-crontab))\n - `flow`: A list of `airduct.scheduling.task`\'s. These can be nested lists, for parallel tasks, 2 levels deep. See example.\n\n`task()` Requires the name of the function you desire to run during that step. Must be defined in the same flow file. You can ignore errors with `can_fail=True` in the function\'s signature.\n\nThis file is placed in a folder/python-module alongside other flows.\n\nTo run: `$ airduct schedule --path /path/to/flow/folder`\n\nBy default it uses a sqlite in-memory database. If using the in-memory database, it will also automatically run as a worker, in addition to a scheduler.\n\n',
    'author': 'Skyler Lewis',
    'author_email': 'skyler.lewis@canopytax.com',
    'url': 'https://github.com/alairock/airduct',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
