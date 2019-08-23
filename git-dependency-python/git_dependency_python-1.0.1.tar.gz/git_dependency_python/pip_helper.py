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

    @staticmethod
    def get_all_pip_dependencies():
        # type: () -> List[str]
        """
        Returns a list of dependencies installed by pip that belong to current python environment.

        :return: A list of pip dependencies.
        """
        try:
            # List all packages installed by pip.
            output = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
        except subprocess.CalledProcessError as ex:
            log_subprocess_err('Failed to list pip packages.', ex)
            return []

        packages = output.decode().split()
        logr.info('Installed packages by pip:\n{}.\n'.format(',\n'.join(packages)))

        return packages
