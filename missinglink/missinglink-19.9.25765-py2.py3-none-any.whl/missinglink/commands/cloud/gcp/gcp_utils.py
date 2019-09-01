# -*- coding: utf-8 -*-

import os


def install_gcp_dependencies():
    from missinglink.commands.utilities.requirement_utils import read_requirements
    from missinglink.sdk import PackageProvider

    file_dir = os.path.dirname(__file__)
    gcp_requirements = read_requirements(file_dir=file_dir, name='gcp')

    package_provider = PackageProvider.get_provider()
    for package in gcp_requirements:
        package_provider.install_package(package)
