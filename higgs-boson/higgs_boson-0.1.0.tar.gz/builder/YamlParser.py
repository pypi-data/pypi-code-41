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
import yaml
from builder import Utils


class PeruBuildTypes:
    TYPE_GIT_MODULE = 'git-module'
    TYPE_CURL_MODULE = 'curl-module'


class YamlDefs:
    DEP = 'dep'
    EXTERNAL = 'external'
    PROJECT = 'project'
    NAME = 'name'
    VERSION = 'version'
    URL = 'url'
    REV = 'rev'
    TYPE = 'type'
    BUILD = 'build'
    LIBS = 'libs'
    INCLUDE = 'include'
    ORDER = 'order'
    UNPACK = 'unpack'


class YamlExternalDep:

    def __init__(self, dep_name: str,  dep_info: dict):
        """
        Constructor used to setup the External Dependency object on
        the provided YAML file entry (represented as a dictionary)
        :param dep_name: String representing the dependency's name
        :param dep_info: Dictionary representing the YAML information
                         for the specified dependency
        """

        # Save the dependency name for later use
        self.__deps_name = dep_name

        # Extract the peru-build related details
        self.__deps_type = None
        self.__deps_details = {}

        # Extract the peru-build related details for Git Modules
        if dep_info.get(YamlDefs.TYPE, None) == PeruBuildTypes.TYPE_GIT_MODULE:
            self.__deps_type = PeruBuildTypes.TYPE_GIT_MODULE
            self.__deps_details[YamlDefs.URL] = dep_info.get(YamlDefs.URL, None)
            self.__deps_details[YamlDefs.REV] = dep_info.get(YamlDefs.REV, None)

        # Extract the peru-build related details for cURL Modules
        if dep_info.get(YamlDefs.TYPE, None) == PeruBuildTypes.TYPE_CURL_MODULE:
            self.__deps_type = PeruBuildTypes.TYPE_CURL_MODULE
            self.__deps_details[YamlDefs.URL] = dep_info.get(YamlDefs.URL, None)
            self.__deps_details[YamlDefs.UNPACK] = dep_info.get(
                YamlDefs.UNPACK, None)

        # Extract build instructions for the dependency
        self.__deps_build_steps = dep_info.get(YamlDefs.BUILD, [])

        # Extract library output information
        # and the desired linking order
        self.__output_libs = dep_info.get(YamlDefs.LIBS, [])
        self.__output_includes = dep_info.get(YamlDefs.INCLUDE, [])
        self.__output_libs_order = dep_info.get(YamlDefs.ORDER, 1)
        self.__output_libs_revision = dep_info.get(YamlDefs.REV, None)

    def get_dependency_name(self) -> str:
        """
        Function used to get the dependency's name
        :return: String representing the dependency's name
        """

        # Get and return the dependency's name
        return self.__deps_name

    def get_peru_import_entry(self) -> str:
        """
        Function used to get the peru build system import entry
        :return: String representing the peru import entry section
        """

        # Build-up and return the peru build system import entry
        return ' ' + str(self.__deps_name) + ': ' + \
               str(self.__deps_name) + '\n'

    def get_peru_module_entry(self) -> str:
        """
        Function used to get the peru build system module entry
        :return: String representing the peru module entry section
        """

        # Create a return object
        ret_module_entry = None

        # Setup the Git-Module Peru Type if that's what type
        # this dependency was configured with
        if self.__deps_type == PeruBuildTypes.TYPE_GIT_MODULE:
            ret_module_entry = '# Setup the import for ' +\
                               str(self.__deps_name) + '\n' +\
                               'git module ' + str(self.__deps_name)\
                               + ':\n' + '  url: ' +\
                               str(self.__deps_details[YamlDefs.URL])\
                               + '\n' + '  rev: ' +\
                               str(self.__deps_details[YamlDefs.REV])\
                               + '\n'

        # Setup the Curl-Module Peru Type if that's what type
        # this dependency was configured with
        if self.__deps_type == PeruBuildTypes.TYPE_CURL_MODULE:
            ret_module_entry = '# Setup the import for ' +\
                               str(self.__deps_name) + '\n' +\
                               'curl module ' + str(self.__deps_name)\
                               + ':\n' + '  url: ' +\
                               str(self.__deps_details[YamlDefs.URL])\
                               + '\n' + '  unpack: ' +\
                               str(self.__deps_details[YamlDefs.UNPACK])\
                               + '\n'

        # Return the return object
        return ret_module_entry

    def get_build_steps(self) -> list:
        """
        Function used to get the build-steps list for the dependency
        :return: List of build steps for the external dependency
        """

        # Get and return the list of build steps from the YAML file
        return self.__deps_build_steps

    def get_built_libs(self) -> list:
        """
        Function used to get the built libraries list for the dependency
        :return: List of built libraries for the external dependency
        """

        # Get and return the list of built libraries from the YAML file
        return self.__output_libs

    def get_lib_includes(self) -> list:
        """
        Function used to get the library includes list for the dependency
        :return: List of library includes for the external dependency
        """

        # Get and return the list of library includes from the YAML file
        return self.__output_includes

    def get_linker_order(self) -> int:
        """
        Function used to get the linker order for the dependency
        :return: Integer representing the linker order for the dependency
        """

        # Get and return the linker order from the YAML file
        return self.__output_libs_order

    def get_linker_revision(self) -> int:
        """
        Function used to get the linker revision for the dependency
        :return: Integer representing the linker revision for the dependency
        """

        # Get and return the linker revision from the YAML file
        return self.__output_libs_revision

    def get_cache_hash(self) -> str:
        """
        Function used to get the SHA256 hash representation of the instance
        for caching purposes (i.e. to tell once instance apart from another)
        :return: String representing the instance's cache-able SHA256 hash
        """

        # Simply hash the string representation of each member and then
        # hash the result of the concatenation of these hashes
        ret_hash = Utils.sha256(str(self.__deps_name))
        ret_hash += Utils.sha256(str(self.__deps_type))
        ret_hash += Utils.sha256(str(self.__deps_details))
        ret_hash += Utils.sha256(str(self.__deps_build_steps))
        ret_hash += Utils.sha256(str(self.__output_libs))
        ret_hash += Utils.sha256(str(self.__output_libs_order))
        ret_hash += Utils.sha256(str(self.__output_libs_revision))
        return Utils.sha256(ret_hash)


class YamlProjectInfo:

    def __init__(self, project_info: dict):
        """
        Constructor used to setup the Project information based on the
        provided YAML information
        :param project_info: Dictionary representing the YAML information
                             for the general higgs project
        """

        # Extract the YAML project definition information
        self.__project_name = project_info.get(YamlDefs.NAME, None)
        self.__project_version = project_info.get(YamlDefs.VERSION, None)

    def get_project_name(self) -> str:
        """
        Function used to get the name of the project
        :return: String representing the project name
        """

        # Return the project's name
        return self.__project_name

    def get_project_version(self) -> str:
        """
        Function used to get the version of the project
        :return: String representing the project version
        """

        # Return the project's version
        return self.__project_version


class YamlParser:

    def __init__(self,
                 yaml_file=os.path.join(Utils.Constants.PROJECT_DIR,
                                        Utils.Constants.HIGGS_FILENAME)):
        """
        Function used to read in (and parse) the provided YAML file according
        to the Higgs YAML standards
        :param yaml_file: String representing the Higgs YAML file to parse
        """

        # Read-in the YAML file contents into the instance
        self.__yaml_file = None
        with open(yaml_file, 'r') as stream:
            self.__yaml_file = yaml.safe_load(stream)

    def get_external_deps(self) -> iter:
        """
        Function used to get all external dependencies for the
        build configuration
        :return: Iterable of ExternalDependency objects representing
                 the external dependencies for the configuration
        """

        # Loop through all of the items in the parsed YAML data
        # looking for the 'dep external' key-words to parse
        for config_item in self.__yaml_file.keys():

            # Parse the key-item for this YAML entry
            key_split = config_item.split(' ')
            if len(key_split) == 3:

                # Check if the key-item conforms to the required
                # standard for external dependencies
                if (key_split[0] == YamlDefs.DEP) and \
                        (key_split[1] == YamlDefs.EXTERNAL):

                    # Create the external dependency object and yield it
                    dep_name = key_split[-1]
                    dep_info = self.__yaml_file.get(config_item)
                    yield YamlExternalDep(dep_name, dep_info)

    def get_higgs_project_def(self) -> YamlProjectInfo:
        """
        Function used to get the list of targets for the build configuration
        :return: YamlProjectInfo representing the project information
        """

        # Create a return object
        ret_object = None

        # Loop through all of the items in the parsed YAML data
        # looking for the 'project' key-word to parse
        for config_item in self.__yaml_file.keys():

            # If we found the 'project' key-word phrase, then parse the YAML
            # information into a Yaml Project Info object to return
            if config_item == YamlDefs.PROJECT:

                # Extract the project information and set it as the return
                project_info = self.__yaml_file.get(config_item)
                ret_object = YamlProjectInfo(project_info)

        # Return the return object
        return ret_object
