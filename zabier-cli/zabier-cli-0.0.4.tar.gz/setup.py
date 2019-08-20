#!/usr/bin/env python

from setuptools import find_packages, setup

setup_options = dict(
    name='zabier-cli',
    version='0.0.4',
    description='A CLI tool to automate Zabbix configurations.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Masashi Terui',
    author_email='terui@serverworks.co.jp',
    url='https://github.com/serverworks/zabier-cli',
    packages=find_packages(exclude=['tests*']),
    install_requires=open('requirements.txt').read().splitlines(),
    entry_points={
        'console_scripts': 'zabier = zabier.cli:main'
    },
    license="MIT License",
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='zabbix automation cli',
)

setup(**setup_options)
