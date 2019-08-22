# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['django_imperavi_redactor']

package_data = \
{'': ['*'],
 'django_imperavi_redactor': ['static/redactor/*',
                              'static/redactor/langs/*',
                              'static/redactor/plugins/alignment/*',
                              'static/redactor/plugins/counter/*',
                              'static/redactor/plugins/filemanager/*',
                              'static/redactor/plugins/fontcolor/*',
                              'static/redactor/plugins/fontsize/*',
                              'static/redactor/plugins/fullscreen/*',
                              'static/redactor/plugins/glvrdplugin/*',
                              'static/redactor/plugins/imagelink/*',
                              'static/redactor/plugins/imagemanager/*',
                              'static/redactor/plugins/inlinestyle/*',
                              'static/redactor/plugins/properties/*',
                              'static/redactor/plugins/quote/*',
                              'static/redactor/plugins/specialchars/*',
                              'static/redactor/plugins/specialtext/*',
                              'static/redactor/plugins/table/*',
                              'static/redactor/plugins/video/*',
                              'static/redactor/plugins/widget/*']}

install_requires = \
['django>=1.11,<3.0']

setup_kwargs = {
    'name': 'django-imperavi-redactor',
    'version': '0.0.1',
    'description': 'Django wrapper for use imperavi redactor.',
    'long_description': '===========================\ndjango-imperavi-redactor\n===========================\n\nThis package is based on the https://bitbucket.org/gearheart/django-redactor package for the old version of imperavi editor.\n\n\n**Warning!!!**\n\n**The editor is not part of the package, as it is proprietary.**\n\nInstallation\n------------\n\n`\npip3 install django-imperavi-redactor==0.0.4a\n`\n\nPut the editor files:\n\n* static/redactor/redactor.min.js\n* static/redactor/redactor.min.css\n',
    'author': 'Dmitry Bastrikin',
    'author_email': 'dima.bastrikin@bro.agency',
    'url': 'https://github.com/brogency/django-imperavi-redactor',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
