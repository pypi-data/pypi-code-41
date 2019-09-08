import logging
import platform
import shutil
import subprocess
import sys

import tabulate

__all__ = ["__version__", "Uninstaller"]

__version__ = '0.2.2'


class Uninstaller:
    """
    Removes the version .Net Core SDK and Runtime.
    """

    def __init__(self):

        if platform.system().lower() == 'windows':
            logging.error("Can only be used in posix systems.")
            sys.exit(1)

        try:
            dotnet_version = subprocess.check_output(["dotnet", "--version"]).strip()
            print(f".Net Version found: {dotnet_version.decode('utf-8')}")
        except FileNotFoundError as e:
            logging.error(".Net Core SDK is not installed")
            sys.exit(1)

    @staticmethod
    def _list_dotnet_sdks():
        dotnet_sdks = subprocess.check_output(["dotnet", "--list-sdks"]).decode('utf-8').split('\n')[:-1]

        return dotnet_sdks

    @staticmethod
    def _list_dotnet_runtimes():
        dotnet_runtimes = subprocess.check_output(["dotnet", "--list-runtimes"]).decode('utf-8').split('\n')[:-1]

        return dotnet_runtimes

    def convert_to_dict(self) -> dict:
        """
        Converts subprocess requests to dictionary.

        :return: A dictionary of version number with its path
        :rtype: dict
        """

        _sdk = []
        _runtime = []

        for sdk in self._list_dotnet_sdks():
            sdk = sdk.split(' ')
            _sdk.append([sdk[0], sdk[1][sdk[1].find("[") + 1: sdk[1].find("]")]])

        for runtime in self._list_dotnet_runtimes():
            runtime = runtime.split(' ')[1:]
            _runtime.append([runtime[0], runtime[1][runtime[1].find("[") + 1: runtime[1].find("]")]])

        out = {
            "sdk": {},
            "runtime": {}
        }
        for key, val in _sdk:
            out['sdk'].setdefault(key, []).append(val + '/' + key)
        for key, val in _runtime:
            out['runtime'].setdefault(key, []).append(val + '/' + key)

        return out

    def delete_sdk(self, version: str = None):
        """
        Deletes the path of the given version, if available.

        :param version: Version number of .Net Core SDK to delete
        """
        converted_dict = self.convert_to_dict()

        if version:
            _sdk_path = converted_dict['sdk'].get(version)
            if not _sdk_path:
                print(f"Paths not found for .Net Core SDK version {version}.")
                sys.exit(1)

            print()
            print(tabulate.tabulate([[p] for p in _sdk_path],
                                    headers=[f"Deleting SDK Version: {version}"],
                                    tablefmt="grid", colalign=("center",)))

            for path in _sdk_path:
                shutil.rmtree(path)

            print("Done.")

    def delete_runtime(self, version: str = None):
        """
        Deletes the path of the given version, if available.

        :param version: Version number of .Net Core Runtime to delete
        """
        converted_dict = self.convert_to_dict()

        if version:
            _runtime_paths = converted_dict['runtime'].get(version)
            if not _runtime_paths:
                print(f"Paths not found for .Net Core Runtime version {version}.")
                sys.exit(1)

            print()
            print(tabulate.tabulate([[p] for p in _runtime_paths],
                                    headers=[f"Deleting Runtime Version: {version}"],
                                    tablefmt="grid", colalign=("center",)))

            for path in _runtime_paths:
                shutil.rmtree(path)

            print("Done.")

    def list_dotnet(self):
        """
        Lists all the installed .Net Core SDKs and Runtimes.
        """
        paths = self.convert_to_dict()

        print()
        print(tabulate.tabulate([[p, "\n".join(v)] for p, v in paths['sdk'].items()], headers=["SDK Version", "Path"],
                                tablefmt="grid", colalign=("center",)))
        print()
        print(tabulate.tabulate([[p, "\n".join(v)] for p, v in paths['runtime'].items()],
                                headers=["Runtime Version", "Path"],
                                tablefmt="grid", colalign=("center",)))
