# coding=utf-8
# Do not import any local modules other than modules beginning with '_'.
# All modules beginning with '_' should follow the same principle

from os.path import dirname, isfile, join

from ._logging_utilities import getLogger


PACKAGE_FILE_NAME = 'PACKAGE_NAME'


def find_package_name(package_directory):
    # type: (str) -> str
    package_name_file_path = join(package_directory, 'data', PACKAGE_FILE_NAME)
    if not isfile(package_name_file_path):
        raise RuntimeError("Unable to determine package name because file at '{}' does not exist.".format(
            package_name_file_path))

    with open(package_name_file_path, 'r') as package_name_file:
        return package_name_file.read()


_package_path = dirname(__file__)
package_name = find_package_name(_package_path)
log = getLogger(package_name)
