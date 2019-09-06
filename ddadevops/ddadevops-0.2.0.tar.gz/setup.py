#!/usr/bin/env python

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'ddadevops',
        version = '0.2.0',
        description = 'dda-devops-build',
        long_description = 'dda-devops-build\n================\n\n|Slack| \\| `\nteam@social.meissa-gmbh.de <https://social.meissa-gmbh.de/@team>`__ \\|\n`Website & Blog <https://domaindrivenarchitecture.org>`__\n\nLicense\n-------\n\nCopyright © 2019 meissa GmbH Licensed under the `Apache License, Version\n2.0 <LICENSE>`__ (the "License")\n\n.. |Slack| image:: https://img.shields.io/badge/chat-clojurians-green.svg?style=flat\n   :target: https://clojurians.slack.com/messages/#dda-pallet/\n',
        author = 'meissa GmbH',
        author_email = 'buero@meissa-gmbh.de',
        license = 'Apache Software License',
        url = 'https://github.com/DomainDrivenArchitecture/dda-devops-build',
        scripts = [],
        packages = ['ddadevops'],
        namespace_packages = [],
        py_modules = [],
        classifiers = [
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.7',
            'Topic :: Software Development :: Build Tools'
        ],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = [],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '',
        obsoletes = [],
    )
