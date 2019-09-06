# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dophon_db',
 'dophon_db.const',
 'dophon_db.mongo',
 'dophon_db.mysql',
 'dophon_db.mysql.orm',
 'dophon_db.mysql.orm.db_obj',
 'dophon_db.mysql.orm.db_obj.function_class',
 'dophon_db.mysql.sql_util',
 'dophon_db.mysql.xml',
 'dophon_db.mysql.xml.binlog',
 'dophon_db.mysql.xml.remote',
 'dophon_db.reader',
 'dophon_db.sqllite',
 'dophon_db.utils']

package_data = \
{'': ['*']}

install_requires = \
['dophon-logger', 'dophon-properties', 'schedule', 'urllib3']

setup_kwargs = {
    'name': 'dophon-db',
    'version': '1.2.8.post2',
    'description': 'dophon database module',
    'long_description': None,
    'author': 'CallMeE',
    'author_email': 'ealohu@163.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
