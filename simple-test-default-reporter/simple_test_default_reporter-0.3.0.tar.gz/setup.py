# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['simple_test_default_reporter',
 'simple_test_default_reporter._vendor',
 'simple_test_default_reporter._vendor.simple_chalk',
 'simple_test_default_reporter._vendor.simple_chalk.src',
 'simple_test_default_reporter._vendor.simple_chalk.src.utils',
 'simple_test_default_reporter._vendor.simple_chalk.src.utils.internal',
 'simple_test_default_reporter._vendor.simple_chalk.tests',
 'simple_test_default_reporter._vendor.tedent',
 'simple_test_default_reporter._vendor.tedent._vendor',
 'simple_test_default_reporter._vendor.tedent._vendor.wrapt',
 'simple_test_default_reporter._vendor.tedent.fns',
 'simple_test_default_reporter._vendor.tedent.fns.decorators',
 'simple_test_default_reporter._vendor.tedent.fns.internal',
 'simple_test_default_reporter._vendor.wrapt',
 'simple_test_default_reporter.fns',
 'simple_test_default_reporter.fns.decorators',
 'simple_test_default_reporter.fns.internal',
 'simple_test_default_reporter.report',
 'simple_test_default_reporter.report.initRootState']

package_data = \
{'': ['*'],
 'simple_test_default_reporter._vendor': ['ordered_set-3.1.1.dist-info/*',
                                          'simple_chalk-0.1.0.dist-info/*',
                                          'tedent-0.1.5.dist-info/*',
                                          'wrapt-1.10.11.dist-info/*'],
 'simple_test_default_reporter._vendor.tedent._vendor': ['ordered_set-3.1.1-py3.7.egg-info/*',
                                                         'wrapt-1.11.1.dist-info/*']}

setup_kwargs = {
    'name': 'simple-test-default-reporter',
    'version': '0.3.0',
    'description': 'The default reporter for simple_test',
    'long_description': 'I will document this module if people will find it helpful.  Currently\nsimple_test is just for my own personal use.\n',
    'author': 'Philip Olson',
    'author_email': 'philip.olson@pm.me',
    'url': 'https://github.com/olsonpm/py_simple-test-default-reporter',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
