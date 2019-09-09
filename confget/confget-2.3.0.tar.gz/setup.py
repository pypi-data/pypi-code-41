#!/usr/bin/python3
#
# Copyright (c) 2019  Peter Pentchev <roam@ringlet.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

"""
Setup infrastructure for confget, the configuration file parser.
"""

import re
import setuptools  # type: ignore


RE_VERSION = r"""^
    \s* VERSION_STRING \s* = \s* "
    (?P<version>
           (?: 0 | [1-9][0-9]* )    # major
        \. (?: 0 | [1-9][0-9]* )    # minor
        \. (?: 0 | [1-9][0-9]* )    # patchlevel
    (?: \. [a-zA-Z0-9]+ )?          # optional addendum (dev1, beta3, etc.)
    )
    " \s*
    $"""


def get_version():
    # type: () -> str
    """ Get the version string from the module's __init__ file. """
    found = None
    re_semver = re.compile(RE_VERSION, re.X)
    with open("confget/defs.py") as init:
        for line in init.readlines():
            match = re_semver.match(line)
            if not match:
                continue
            assert found is None
            found = match.group("version")

    assert found is not None
    return found


def get_long_description():
    # type: () -> str
    """ Get the package long description from the README file. """
    with open("README.md") as readme:
        return readme.read()


setuptools.setup(
    name="confget",
    version=get_version(),
    description="Parse configuration files and extract values from them",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Peter Pentchev",
    author_email="roam@ringlet.net",
    url="https://devel.ringlet.net/textproc/confget/",
    packages=["confget", "confget.backend"],
    package_data={
        "confget": [
            # The typed module marker
            "py.typed"
        ]
    },
    install_requires=['configparser;python_version<"3"', "six"],
    license="BSD-2",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: DFSG approved",
        "License :: Freely Distributable",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    entry_points={"console_scripts": ["confget=confget.__main__:main"]},
    zip_safe=True,
)
