# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['windmill',
 'windmill.cli',
 'windmill.config',
 'windmill.http',
 'windmill.http.api',
 'windmill.models',
 'windmill.models.dags',
 'windmill.models.operators',
 'windmill.models.schemas',
 'windmill.tasks',
 'windmill.utils']

package_data = \
{'': ['*'],
 'windmill.http': ['app/*',
                   'app/dist/*',
                   'app/public/*',
                   'app/src/*',
                   'app/src/components/*',
                   'app/src/components/Airflow/*',
                   'app/src/components/Navbar/*',
                   'app/src/components/Page/*',
                   'app/src/components/Sidebar/*',
                   'app/src/misc/*']}

install_requires = \
['apache-airflow[crypto,celery,postgres,hive,jdbc,mysql,ssh]==1.10.4',
 'decli>=0.5.0,<0.6.0',
 'docstring-parser>=0.3.0,<0.4.0',
 'flask-cors>=3.0.8,<4.0.0',
 'marshmallow>=3.0,<4.0',
 'pyyaml>=5.1.2,<6.0.0']

entry_points = \
{'console_scripts': ['windmill = windmill:cli.cli.Cli.run_cli',
                     'windmill-dev = windmill:cli.cli.DevCli.run_cli']}

setup_kwargs = {
    'name': 'windmill-airflow',
    'version': '0.0.2',
    'description': '',
    'long_description': "# Windmill\n\nDrag'n'drop web app to manage and create Airflow DAGs. The goal is to\nhave a Web UI that can generate YML Dag Definitions, integrating with\ncustom operators and potentially existing DAGs. YML DAGs can then be\nsynced to a remote repo\n\n- Front end is built using Typescript React\n- Back end is built using Flask on Python 3.6+\n\n## MVP Required Features\n\n### Front-End Features\n\n- [x] Dynamic Operators\n- [x] Menu Dropdowns\n- [x] Load Operators from App\n- [x] Format operator display into classes\n- [x] Search functionality for operators\n- [x] Basic operator level properties\n- [x] Implement DAG level properties\n- [x] New DAG Functionality\n- [x] Parameter Tooltips\n- [x] Render arbitrary viewport windows for New/Save/Load etc\n- [x] Overwrite/Save prompt on New\n- [x] DAG renaming and save functionality\n- [ ] Open dag from menu\n- [ ] Check if file already exists on rename\n- [ ] Prompt save if there are nodes on open\n- [ ] Fix loss of state on refresh bug\n- [ ] Icons\n- [ ] Put File details in File Browser \n- [ ] Pull PORT from Flask host\n- [ ] Add a last saved time to NavBar\n\n### Back-End Features\n\n- [x] Generate Operator Lists\n- [x] CLI to start Web and Front End\n- [x] Generate DAG Spec\n- [x] CLI to create new windmill project\n- [x] CLI to start windmill from a windmill project\n- [x] Implement windmill-dev start\n- [x] Save/Load Windmill Files functionality\n- [ ] Validate incoming WMLs (is there a need for this?)\n- [x] Get default values\n- [x] Pull parameters from parent classes\n- [?] Dedupe multi import operators - nothing preventing this but underlying issue is fixed\n- [ ] Get WML owner and last-modified details during wml list\n- [ ] Allow custom operators\n- [ ] Add defaults to CLI --help commands\n- [ ] Strategy for Python Opjects (e.g. callables) - maybe import statement?\n- [ ] Backport existing Python DAGs to WMLs\n- [ ] Allow YML updates to propogate to WMLs\n- [ ] Allow user specified Airflow Version - isolate to docker or something so we can run 2.7 if we want?\n\n## MVP Usage Pattern\n\nTo run as a user:\n\n1. Install with `pip install airflow-windmill`\n2. Run `windmill init` to create a local Windmill project\n3. Run `windmill run` from this folder to run the app locally\n\nTo run as a dev:\n\n1. Clone from git\n2. Run `poetry install`\n3. ?Run `windmill-dev install-node-depts`\n4. Run `windmill-dev start` to start a flask server and use parcel to serve frontend\n\n## Future Usage Patterns\n\n- Auto-sync for windmill project to git\n\n## Getting Started\n\nThis package can be installed and run using Pip:\n\n```\npip install windmill-airflow\n```\n\n## Deployment\n\n```bash\n# Run NPM build\ncd windmill/http/app/\nnpm run-script build\n\n# Update git ...\ncd ../../../\n\n# Poetry build\npoetry build\npoetry publish\n```",
    'author': 'mayansalama',
    'author_email': 'micsalama@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
