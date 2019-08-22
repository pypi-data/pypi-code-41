#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
import re
from os import path
from pathlib import Path

from pkg_resources import resource_filename
from psyko.browser_fetcher import chromium_executable, download_chromium
from setuptools import find_packages, setup
from setuptools.command.install import install

with open('README.md') as readme_file:
    readme = readme_file.read()


_version_re = re.compile(r'__version__\s+=\s+(.*)')


with open('psyko/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

print(path.dirname(path.abspath(__file__)))

requirements = ['pychrome==0.2.3']


class PostInstallCommand(install):
    def run(self):
        c = Path(chromium_executable())
        if not c.exists():
            download_chromium()
        install.run(self)


setup(
    name='psyko',
    version=version,
    description="A Python port of Taiko",
    long_description=readme,
    author="BugDiver",
    author_email='vinayshankar00@gmail.com',
    url='https://github.com/BugDiver/taiko-py',
    packages=find_packages(),
    package_dir={},
    entry_points={
        'console_scripts': ['psyko = psyko.cli:main']
    },
    cmdclass={
        'install': PostInstallCommand
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='psyko',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Browsers'
    ],
)
