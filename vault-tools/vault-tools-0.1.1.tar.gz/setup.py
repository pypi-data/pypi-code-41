#!/usr/bin/env python
import configparser

from setuptools import find_packages, setup

SRC_PREFIX = 'src'

packages = find_packages(SRC_PREFIX)


def get_required_packages():
    """
    Returns the packages used for install_requires

    This used to pin down every package in Pipfile.lock to the version, but that, in turn, broke
    downstream projects because it was way too strict.

    Now, this simply grabs all the items listed in the `Pipfile` `[packages]` section without version
    pinning
    """
    config = configparser.ConfigParser(strict=False)
    config.read('Pipfile')

    install_requires = sorted([x for x in config['packages']])

    return install_requires


def readme():
    with open('README.md') as f:
        return f.read()


if __name__ == '__main__':
    setup(
        name='vault-tools',
        url='https://github.com/openslate/vault-tools',
        author='OpenSlate',
        author_email='code@openslate.com',
        version='0.1.1',
        description='misc tools to work with vault',
        long_description=readme(),
        long_description_content_type='text/markdown',
        package_dir={'': 'src'},
        packages=packages,
        entry_points={
            'console_scripts': [
                'process-vault-environment = vault_tools.entrypoints:process_vault_environment',
                'renew-token = vault_tools.entrypoints:renew_token',
            ],
        },
        scripts=[
            'scripts/write-vault-environment',
        ],
        install_requires=get_required_packages()
    )
