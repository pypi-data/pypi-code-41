# This file is part of Higgs Boson.
#
# Copyright (c) BitBoson
#
# Higgs Boson is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Higgs Boson is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Higgs Boson.  If not, see <https://www.gnu.org/licenses/>.
#
# Written by:
#     - Tyler Parcell <OriginLegend>
#

import os
import sys
import hashlib


# Upon import, get the current script location as the default for
# any and all-project relative files/directories
class Constants:
    PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(
        os.path.realpath(__file__)), os.pardir))
    LOG_OK = 'OK'
    LOG_SKIP = 'SKIP'
    LOG_FAIL = 'FAILED'
    SRC_DIR = 'src'
    TEST_DIR = 'test'
    CMAKE_LISTS_TXT = 'CMakeLists.txt'
    HIGGS_FILENAME = 'higgs-boson.yaml'
    HIGGS_BUILD_TARGET = 'higgs-build-target'
    HIGGS_TEST_TARGET = 'higgs-test-target'
    HIGGS_COVERAGE_TARGET = 'higgs-coverage-target'
    HIGGS_PACKAGE_TARGET = 'higgs-package-target'
    HIGGS_TEMP_DIR = '.higgs-boson'
    HIGGS_DEPS_DIR = 'external'
    HIGGS_OUT_DIR = 'output'
    HIGGS_INC_DIR = 'include'
    HIGGS_LIB_DIR = 'libs'
    HIGGS_BUILD_DIR = 'build'
    HIGGS_TEST_DIR = 'test'
    HIGGS_COVERAGE_DIR = 'coverage'
    HIGGS_HASH_FILE = '.higgs-build-cache-file'
    HIGGS_BUILD_FILE = 'higgs-build-script.sh'
    LIBRARY_FILE_EXTENSIONS = ['so', 'dll']
    HEADER_FILE_EXTENSIONS = ['h', 'hpp', 'i', 'ipp']
    SOURCE_FILE_EXTENSIONS = ['c', 'cpp', 'cxx', 'c++']


# Setup a simple sha256 function for simple hashing
def sha256(message: str) -> str:
    """
    Function used to get the SHA256 representation of the given
    string message
    :param message: String representing the message to hash
    :return: String representing the SHA256 hash of the message
    """
    return str(hashlib.sha256(message.encode('utf-8')).hexdigest())


# Setup a tprint method for printing to the terminal
def tprint(message: str, newline=False) -> None:
    """
    Function used to print the message to the terminal
    :param message: String representing the message to print
    :param newline: Boolean indicating whether to add a newline
                    or not after printing the message
    :return: None
    """

    # Use the system std-out write to print the message
    sys.stdout.write(message)

    # Add-in the newline character if desired
    if newline:
        sys.stdout.write('\n')

    # Flush the std-out buffer
    sys.stdout.flush()


# Setup function for recursively searching a directory
def get_files_in_directory(dir_location: str, valid_extensions=None) -> iter:
    """
    Function used to recursively search a directory for all files with the
    provided extensions (if None, then all files are returned)
    :param dir_location:
    :param valid_extensions:
    :return:
    """
    for root, dirs, files in os.walk(dir_location):
        for file in files:
            if valid_extensions is None or \
                    file.split('.')[-1] in valid_extensions:
                yield os.path.join(root, file)
