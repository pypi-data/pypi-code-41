"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of fe3h-checklist.

fe3h-checklist is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

fe3h-checklist is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with fe3h-checklist.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

import os
import shutil
from setuptools import setup, find_packages
from fe3h_checklist import local_dir, support_levels_file, \
    support_levels_info_file

if __name__ == "__main__":
    setup(
        name="fe3h-checklist",
        version=open("version", "r").read(),
        description="A checklist for Fire Emblem Three Houses",
        long_description=open("README.md", "r").read(),
        long_description_content_type="text/markdown",
        author="Hermann Krumrey",
        author_email="hermann@krumreyh.com",
        classifiers=[
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
        ],
        url="https://gitlab.namibsun.net/namibsun/python/fe3h-checklist",
        license="GNU GPL3",
        packages=find_packages(),
        scripts=list(map(lambda x: os.path.join("bin", x), os.listdir("bin"))),
        install_requires=[
            "typing",
            "colorama",
            "pyexcel_ods"
        ],
        test_suite='nose.collector',
        tests_require=['nose'],
        include_package_data=True,
        zip_safe=False
    )

if not os.path.isdir(local_dir):
    os.makedirs(local_dir)
if not os.path.isfile(support_levels_info_file):
    shutil.copyfile(
        "fe3h_checklist/data/support_levels_info.ods",
        support_levels_info_file
    )
if not os.path.isfile(support_levels_file):
    shutil.copyfile(
        "fe3h_checklist/data/support_levels.ods",
        support_levels_file
    )
