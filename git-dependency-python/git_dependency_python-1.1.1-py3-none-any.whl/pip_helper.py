import subprocess
import sys
import logging

from typing import List
from git_dependency_python.tools import log_subprocess_err

logr = logging.getLogger(__name__)


class PipHelper:
    """
    Class for installing external dependencies via pip.
    """
    @staticmethod
    def install_by_pip(dependency):
        # type: (str) -> None
        """
        Installs package with pip package manager.

        :param dependency: Package to install. E.g. "pip==18.1".

        :return: No return.
        """
        # Install dependency through pip
        command = [sys.executable, "-m", "pip", "install", dependency]

        try:
            subprocess.check_call(command)
        except subprocess.CalledProcessError as ex:
            log_subprocess_err('Failed to install dependency {} from pip'.format(dependency), ex)
            raise

