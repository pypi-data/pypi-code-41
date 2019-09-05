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
    'version': '0.1.12',
    'description': 'Simple Pipeline Scheduler in Python',
    'long_description': "# airduct\nSimple Pipeline Scheduler in Python\n\n![Airduct Screenshot](docs/screenshot.png)\n\n## Links\n\n- [Github](https://github.com/alairock/airduct)\n- [Documentation](https://airduct.readthedocs.io)\n\n## Installing\n    $ pip install airduct\n\nor\n\n    $ poetry add airduct\n\n## Quickstart\n\nCreate a file and put into a folder/python-module.\n\n```python\nfrom airduct import schedule, task\n\n\nschedule(\n    name='ExampleFlow',\n    run_at='* * * * *',\n    flow=[\n        task('e1f1'),\n        [task('e1f2'), task('e1f3', can_fail=True)],\n        [task('e1f4')]\n    ]\n)\n\nasync def e1f1():\n    print('e1f1 - An async function!')\n\ndef e1f2():\n    print('e1f2 - Regular functions work too')\n\nasync def e1f3():\n    print('e1f3')\n\nasync def e1f4():\n    print('e1f4')\n```\n\nRun: `$ airduct schedule --path /path/to/folder`\n\nBy default it uses a sqlite in-memory database. If using the in-memory database, it will also automatically run as a worker, in addition to a scheduler. If you wish to use a non in-memory sqlite database, you will need to also run a worker (could be on same box, or separate) See the documentation for more info.\n\n",
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
