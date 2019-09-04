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
import ntpath
import subprocess
from builder import Utils
from builder import YamlParser


class DependencyBuildManager:

    def __init__(self, yaml_info: YamlParser,
                 base_project_dir=Utils.Constants.PROJECT_DIR,
                 temp_directory=Utils.Constants.HIGGS_TEMP_DIR):
        """
        Constructor used to initialize the Dependency Build Manager
        :param yaml_info: Yaml Parser representing the YAML file contents
        :param base_project_dir: String representing the project directory
        :param temp_directory: String representing the temp Higgs location
        """

        # Simply save a reference to the Higgs Config
        # and the base project directory
        self.__yaml_parser = yaml_info
        self.__base_project_dir = base_project_dir
        self.__temp_directory = temp_directory

    def get_external_deps_list(self) -> list:
        """
        Function used to get a list of external dependencies
        :return: List representing the names of the external dependencies
        """

        # Create a return list
        ret_list = []

        # Add all of the external dependencies to the return list
        for external_dep in self.__yaml_parser.get_external_deps():
            ret_list.append(external_dep.get_dependency_name())

        # Return the return list
        return ret_list

    def build_external_dependency(self, dep_name: str) -> tuple:
        """
        Function used to build the given external dependency
        NOTE: This will only build external dependencies
        :param dep_name: String representing the dependency name
        :return: (Boolean, Boolean) Tuple indicating whether the
                 operation was successful and whether it was skipped
        """

        # Create a return flag
        ret_flag = False
        was_skipped = False

        # Attempt to get the external dependency object from the
        # internal Higgs config object
        external_dependency = None
        for external_dep in self.__yaml_parser.get_external_deps():
            if external_dep.get_dependency_name() == dep_name:
                external_dependency = external_dep
                break

        # Only continue if the external dependency was found
        if external_dependency is not None:

            # First check if the dependency needs built by checking the
            # cache of already-built dependencies
            needs_built = True
            higgs_build_cache = os.path.join(self.__base_project_dir,
                                              self.__temp_directory,
                                              Utils.Constants.HIGGS_DEPS_DIR,
                                              dep_name,
                                              Utils.Constants.HIGGS_HASH_FILE)
            if os.path.isfile(higgs_build_cache):
                with open(higgs_build_cache, 'r') as cache_file:
                    cache_hash = cache_file.read()
                    if cache_hash == external_dependency.get_cache_hash():
                        needs_built = False
                        ret_flag = True
                        was_skipped = True

            # Only continue if this dependency actually needs built
            if needs_built:

                # Open and write the build script for building the dependency
                build_script_loc = os.path.join(self.__base_project_dir,
                                                self.__temp_directory,
                                                Utils.Constants.HIGGS_DEPS_DIR,
                                                dep_name)
                build_script_file = os.path.join(
                    build_script_loc,
                    Utils.Constants.HIGGS_BUILD_FILE)
                with open(build_script_file, 'w') as build_script:

                    # First write in the change-directory command for building
                    build_script.write('cd ' + str(build_script_loc)
                                       + str('\n'))

                    # Add in the specified build steps from the YAML file
                    for build_step in external_dependency.get_build_steps():
                        build_script.write(build_step + str('\n'))

                # Run the build-script to build the dependency
                process = None
                try:
                    process = subprocess.Popen(['sh', str(build_script_file)])
                    process.wait()
                    ret_flag = True
                except Exception:
                    error_msg = process.stdout.read()
                    Utils.tprint('\n' + str(error_msg), newline=True)

                # If the build was successful, write the build-cache info
                if ret_flag:
                    with open(higgs_build_cache, 'w') as cache_file:
                        cache_file.write(external_dependency.get_cache_hash())

        # Return the return flag
        return ret_flag, was_skipped

    def get_external_dependency_includes(self, dep_name: str) -> iter:
        """
        Function used to get an iterable of include files (headers) from
        the external dependency
        :param dep_name: String representing the dependency name
        :return: Iterable of 2-Tuples representing the header files
                 as well as the relative directory they are in
        """

        # Attempt to get the external dependency object from the
        # internal Higgs config object
        external_dependency = None
        for external_dep in self.__yaml_parser.get_external_deps():
            if external_dep.get_dependency_name() == dep_name:
                external_dependency = external_dep
                break

        # Only continue if the external dependency was found
        if external_dependency is not None:

            # Get a list of all of the include directories in the YAML
            include_dirs = external_dependency.get_lib_includes()

            # Prepend the actual location of the dependency to each include
            base_include_dir = os.path.join(self.__base_project_dir,
                                            self.__temp_directory,
                                            Utils.Constants.HIGGS_DEPS_DIR)
            tmp_include_list = []
            for include_dir in include_dirs:
                tmp_include_list.append((os.path.join(base_include_dir,
                                                      dep_name, include_dir),
                                         include_dir))
            include_dirs = tmp_include_list

            # If the include directories is empty, then add the base directory
            # for the external dependency as the only search directory
            if len(include_dirs) == 0:
                include_dirs = [(os.path.join(base_include_dir, dep_name),
                                 None)]

            # Loop through all of the include directories, then for each,
            # recursively walk the file-tree looking for header files
            # TODO - Make the header extensions configurable
            for include_dir in include_dirs:
                for include_file in Utils.get_files_in_directory(
                        include_dir[0],
                        Utils.Constants.HEADER_FILE_EXTENSIONS):

                    # Correct the relative path if present
                    rel_path = include_dir[1]
                    if rel_path is not None:
                        if include_file.startswith(include_dir[0]):

                            # First deduce the relative path including the
                            # header file itself
                            rel_path = include_file[len(include_dir[0]):]
                            if rel_path[0] == os.path.sep:
                                rel_path = rel_path[1:]

                            # Next, remove the header file leaving only
                            # the relative directory for copying it into
                            header_name = ntpath.basename(rel_path)
                            rel_path = rel_path[:-1 * (len(header_name) + 1)]

                    # Yield the header and relative path
                    yield include_file, rel_path
