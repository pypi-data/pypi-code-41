# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['simple_test_process',
 'simple_test_process._vendor',
 'simple_test_process._vendor.po',
 'simple_test_process._vendor.po.case_conversion',
 'simple_test_process._vendor.simple_test_default_reporter',
 'simple_test_process._vendor.simple_test_default_reporter._vendor',
 'simple_test_process._vendor.simple_test_default_reporter._vendor.simple_chalk',
 'simple_test_process._vendor.simple_test_default_reporter._vendor.simple_chalk.src',
 'simple_test_process._vendor.simple_test_default_reporter._vendor.simple_chalk.src.utils',
 'simple_test_process._vendor.simple_test_default_reporter._vendor.simple_chalk.src.utils.internal',
 'simple_test_process._vendor.simple_test_default_reporter._vendor.simple_chalk.tests',
 'simple_test_process._vendor.simple_test_default_reporter._vendor.tedent',
 'simple_test_process._vendor.simple_test_default_reporter._vendor.tedent._vendor',
 'simple_test_process._vendor.simple_test_default_reporter._vendor.tedent._vendor.wrapt',
 'simple_test_process._vendor.simple_test_default_reporter._vendor.tedent.fns',
 'simple_test_process._vendor.simple_test_default_reporter._vendor.tedent.fns.decorators',
 'simple_test_process._vendor.simple_test_default_reporter._vendor.tedent.fns.internal',
 'simple_test_process._vendor.simple_test_default_reporter._vendor.wrapt',
 'simple_test_process._vendor.simple_test_default_reporter.fns',
 'simple_test_process._vendor.simple_test_default_reporter.fns.decorators',
 'simple_test_process._vendor.simple_test_default_reporter.fns.internal',
 'simple_test_process._vendor.simple_test_default_reporter.report',
 'simple_test_process._vendor.simple_test_default_reporter.report.initRootState',
 'simple_test_process._vendor.tedent',
 'simple_test_process._vendor.tedent._vendor',
 'simple_test_process._vendor.tedent._vendor.wrapt',
 'simple_test_process._vendor.tedent.fns',
 'simple_test_process._vendor.tedent.fns.decorators',
 'simple_test_process._vendor.tedent.fns.internal',
 'simple_test_process._vendor.toml',
 'simple_test_process._vendor.wrapt',
 'simple_test_process.fns',
 'simple_test_process.fns.decorators',
 'simple_test_process.fns.internal']

package_data = \
{'': ['*'],
 'simple_test_process._vendor': ['ordered_set-3.1.1.dist-info/*',
                                 'po.case_conversion-0.2.0.dist-info/*',
                                 'simple_test_default_reporter-0.2.1.dist-info/*',
                                 'tedent-0.1.5.dist-info/*',
                                 'toml-0.10.0.dist-info/*',
                                 'wrapt-1.10.11.dist-info/*'],
 'simple_test_process._vendor.simple_test_default_reporter._vendor': ['ordered_set-3.1.1.dist-info/*',
                                                                      'simple_chalk-0.1.0.dist-info/*',
                                                                      'tedent-0.1.5.dist-info/*',
                                                                      'wrapt-1.10.11.dist-info/*'],
 'simple_test_process._vendor.simple_test_default_reporter._vendor.tedent._vendor': ['ordered_set-3.1.1-py3.7.egg-info/*',
                                                                                     'wrapt-1.11.1.dist-info/*'],
 'simple_test_process._vendor.tedent._vendor': ['ordered_set-3.1.1-py3.7.egg-info/*',
                                                'wrapt-1.11.1.dist-info/*']}

setup_kwargs = {
    'name': 'simple-test-process',
    'version': '0.4.5',
    'description': 'The process ran by simple_test to isolate the environment',
    'long_description': 'I will document this module if people will find it helpful.  Currently\nsimple_test is just for my own personal use.\n',
    'author': 'Philip Olson',
    'author_email': 'philip.olson@pm.me',
    'url': 'https://github.com/olsonpm/py_simple-test-process',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
