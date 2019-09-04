"""Utility for PEP 440 compliant versions."""

__all__ = (
    "Version",
)

import os
import datetime
import subprocess
import collections

VersionBase = collections.namedtuple("VersionBase", (
    "major", "minor", "micro", "name", "dev"
))


class Version(VersionBase):
    """
    Version tuple that converts to PEP 440 compliant string.

    Based on django's versioning system.
    """
    __slots__ = ()

    _version = None

    def __new__(cls, *version):
        """
        Create a new tuple.

        :param version: The version tuple
        :type version: any

        :return: A new Version instance
        :rtype: Version
        """
        cls._version = cls._get_version(version)
        return super().__new__(cls, *version)

    def __str__(self):
        """Return the actual PEP-440 compliant string."""
        return self._version

    @classmethod
    def _get_version(cls, arguments):
        """
        Retrieve the PEP 440-compliant version string.

        :param arguments: The arguments for the version
        :type arguments: tuple

        :return: The generated version string
        :rtype: str
        """
        assert arguments[3] in ('alpha', 'beta', 'rc', 'final')

        size = 2 if arguments[2] == 0 else 3
        main = ".".join(str(c) for c in arguments[:size])

        if arguments[3] == "alpha" and arguments[4] == 0:
            return main + ".dev" + cls._get_commit_timestamp()

        if arguments[3] != "final":
            code = "rc" if arguments[3] == "rc" else arguments[3][0]
            return main + code + str(arguments[4])

        return main

    @classmethod
    def _get_commit_timestamp(cls):
        """
        Retrieve the timestamp of the last commit.

        :return: The timestamp of the last commit
        :rtype: str
        """
        current = os.path.dirname(os.path.abspath(__file__))
        process = subprocess.Popen(
            "git log --pretty=format:%ct --quiet -1 HEAD",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            shell=True, cwd=current, universal_newlines=True,
        )

        timestamp = int(process.communicate()[0])
        timestamp = datetime.datetime.utcfromtimestamp(timestamp)

        return timestamp.strftime('%Y%m%d%H%M%S')
