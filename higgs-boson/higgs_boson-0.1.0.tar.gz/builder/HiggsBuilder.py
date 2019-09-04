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
import shutil
import ntpath
import subprocess
from builder import Utils
from builder import YamlParser
from builder import PeruManager
from builder import DependencyBuildManager


class HiggsBuilder:

    def __init__(self, base_project_dir=Utils.Constants.PROJECT_DIR,
                 yaml_file=Utils.Constants.HIGGS_FILENAME,
                 temp_dir=Utils.Constants.HIGGS_TEMP_DIR):
        """
        Constructor used to facilitate the entire Higgs build process
        :param base_project_dir: String representing the project directory
        :param yaml_file: String representing the YAML file path
        """

        # Setup the Yaml Parser to parse the YAML file
        self.__yaml_info = YamlParser.YamlParser(yaml_file=yaml_file)

        # Setup other important references
        self.__base_project_dir = base_project_dir
        self.__temp_dir = temp_dir
        self.__output_libs_dir = os.path.join(
            self.__base_project_dir, temp_dir, Utils.Constants.HIGGS_DEPS_DIR,
            Utils.Constants.HIGGS_OUT_DIR, Utils.Constants.HIGGS_LIB_DIR)
        self.__output_include_dir = os.path.join(
            self.__base_project_dir, temp_dir, Utils.Constants.HIGGS_DEPS_DIR,
            Utils.Constants.HIGGS_OUT_DIR, Utils.Constants.HIGGS_INC_DIR)
        self.__build_dir = os.path.join(
            self.__base_project_dir, temp_dir, Utils.Constants.HIGGS_BUILD_DIR)

        # Make all required directories if they don't exist
        if not os.path.exists(self.__temp_dir):
            os.makedirs(self.__temp_dir)
        if not os.path.exists(self.__output_libs_dir):
            os.makedirs(self.__output_libs_dir)
        if not os.path.exists(self.__output_include_dir):
            os.makedirs(self.__output_include_dir)

        # Setup all None objects until defined later
        self.__peru_manager = None
        self.__ext_deps_builder = None

        # Extract the library output information and link order
        self.__linker_info = {}
        for external_dep in self.__yaml_info.get_external_deps():
            link_info = {YamlParser.YamlDefs.LIBS:
                         external_dep.get_built_libs(),
                         YamlParser.YamlDefs.ORDER:
                         external_dep.get_linker_order(),
                         YamlParser.YamlDefs.REV:
                         external_dep.get_linker_revision()}
            self.__linker_info[external_dep.get_dependency_name()] = link_info

    def download_deps(self) -> bool:
        """
        Function used to download all dependencies via the use of Peru
        :return: Boolean indicating whether the process was successful or not
        """

        # Create a return flag
        ret_flag = False

        # Indicate that we are downloading dependencies
        Utils.tprint('Downloading External Dependencies ... ')

        # Setup the Peru object on the internal builder and run the sync
        if self.__peru_manager is None:
            self.__peru_manager = PeruManager.PeruManager(
                yaml_info=self.__yaml_info,
                base_project_dir=self.__base_project_dir,
                temp_directory=self.__temp_dir)

        # Actually start downloading the dependencies using Peru
        # and keep track of the results (if successful)
        self.__peru_manager.write_peru_file()
        if self.__peru_manager.peru_sync():
            Utils.tprint(Utils.Constants.LOG_OK, newline=True)
            ret_flag = True

        # Return the return flag
        return ret_flag

    def build_external_deps(self) -> bool:
        """
        Function used to build all external dependencies via the YAML config
        :return: Boolean indicating whether the process was successful or not
        """

        # Create a return flag
        ret_flag = True

        # Setup the External Dependencies Builder object
        if self.__ext_deps_builder is None:
            self.__ext_deps_builder = DependencyBuildManager.\
                DependencyBuildManager(yaml_info=self.__yaml_info,
                                       base_project_dir=self.__base_project_dir)

        # List all of the external dependencies
        # TODO - Parallelize external dependency builds
        for ext_dep in self.__ext_deps_builder.get_external_deps_list():

            # Indicate which external dependency we are on and build it
            Utils.tprint('Building External Dependency: ' +
                         str(ext_dep) + ' ... ')
            res, skipped = self.__ext_deps_builder.build_external_dependency(
                ext_dep)

            # If the output directory for the library doesn't exist,
            # create it now
            library_output_path = os.path.join(self.__output_libs_dir,
                                               ext_dep)
            if not os.path.exists(os.path.join(library_output_path)):
                os.makedirs(library_output_path)

            # If the operation was successful, copy the output libraries to
            # the general output directory for external dependencies
            if res:
                linker_info = self.__linker_info.get(ext_dep, {})
                for out_lib in linker_info.get(YamlParser.YamlDefs.LIBS, []):

                    # If the copied library doesn't end in a version number
                    # (just the .so extension) then append the revision
                    # information (unless it doesn't exist - then just ignore)
                    out_lib_dest = ntpath.basename(out_lib)
                    curr_rev = linker_info.get(YamlParser.YamlDefs.REV, None)
                    if (out_lib_dest.split('.')[-1] in
                        Utils.Constants.LIBRARY_FILE_EXTENSIONS) and \
                            (curr_rev is not None):
                        out_lib_dest = '.'.join([out_lib_dest, curr_rev])

                    # Actually perform the copy operation
                    shutil.copyfile(os.path.join(
                        self.__base_project_dir, self.__temp_dir,
                        Utils.Constants.HIGGS_DEPS_DIR, ext_dep, out_lib),
                                    os.path.join(library_output_path,
                                                 out_lib_dest))

                # Ensure that the dependency-specific include directory exists
                include_dir_output = os.path.join(self.__output_include_dir,
                                                  ext_dep)
                if not os.path.exists(include_dir_output):
                    os.makedirs(include_dir_output)

                # Now that we have all of the libraries copied over,
                # we must copy all of the header files over
                deps_builder = self.__ext_deps_builder
                for header in deps_builder.get_external_dependency_includes(
                        ext_dep):

                    # If no relative path was specified, put the header in
                    # the default output/include location
                    if header[1] is None:
                        shutil.copy2(header[0], include_dir_output)

                    # If a relative path was specified, put the header in
                    # the relative output/include location
                    else:

                        # Ensure the relative path exists
                        dest_path = os.path.join(include_dir_output,
                                                 header[1])
                        if not os.path.exists(dest_path):
                            os.makedirs(dest_path)

                        # Actually copy the file into the relative path
                        shutil.copy2(header[0], dest_path)

            # If the operation was successful, print that, otherwise, exit
            # the loop early and set the return flag to false
            if res and skipped:
                Utils.tprint(Utils.Constants.LOG_SKIP, newline=True)
            elif res and not skipped:
                Utils.tprint(Utils.Constants.LOG_OK, newline=True)
            else:
                ret_flag = False
                break

        # If the operation was successful, remove the build directory
        if ret_flag:
            if os.path.exists(self.__build_dir):
                shutil.rmtree(self.__build_dir)

        # Return the return flag
        return ret_flag

    def create_external_cmake_lists(self) -> None:
        """
        Function used to create the internal Higgs Managed CMakeLists.txt
        file for including into the main CMakeLists.txt file project
        :return: None
        """

        # Start by removing any existing CMakeLists.txt file in the
        # Higgs temporary directory
        higgs_cmake_file = os.path.join(self.__base_project_dir,
                                         self.__temp_dir,
                                         Utils.Constants.CMAKE_LISTS_TXT)
        if os.path.isfile(higgs_cmake_file):
            os.remove(higgs_cmake_file)

        # Extract the relevant YAML project information
        project_yaml_info = self.__yaml_info.get_higgs_project_def()
        project_name = project_yaml_info.get_project_name().lower()
        project_version = project_yaml_info.get_project_version()

        # Create and open the Higgs CMake File so we can write to it
        with open(higgs_cmake_file, 'w') as cmake_file:

            # Write in the edit/auto-generation warning
            cmake_file.write('# THIS IS AN AUTOGENERATED FILE USING HIGGS\n')
            cmake_file.write('# DO NOT EDIT (UNLESS YOU KNOW WHAT\'S UP)\n')
            cmake_file.write('\n')

            # Write in the minimum CMake Version for the project
            cmake_file.write('# Setup the CMake minimum requirements\n')
            cmake_file.write('cmake_minimum_required(VERSION 3.0.0)\n')
            cmake_file.write('\n')

            # Write in the C++ Standard
            # TODO - Generalize to specify C++ Standard
            cmake_file.write('# Set C++17 standard\n')
            cmake_file.write('set(CMAKE_CXX_STANDARD 17)\n')
            cmake_file.write('\n')

            # Write in Higgs-Specific variables
            cmake_file.write('# Higgs Build Variables\n')
            cmake_file.write('set(HIGGS_PROJECT_NAME "'
                             + str(project_name) + '")\n')
            cmake_file.write('set(HIGGS_PROJECT_SRC "'
                             + str(self.__base_project_dir) + '")\n')
            cmake_file.write('set(HIGGS_PROJECT_VERSION "'
                             + str(project_version) + '")\n')
            cmake_file.write('\n')

            # Write in the Project Specifics
            cmake_file.write('# Project Specifics\n')
            cmake_file.write('set(PROJECTNAME "${HIGGS_PROJECT_NAME}")\n')
            cmake_file.write('project(${PROJECTNAME} CXX)\n')
            cmake_file.write('\n')

            # Write in the Project Main Targets
            cmake_file.write('# Project Main Targets\n')
            cmake_file.write('set(PROJECT_TARGET_MAIN "${PROJECTNAME}")\n')
            cmake_file.write('set(PROJECT_TARGET_TEST "${PROJECTNAME}_test")\n')
            cmake_file.write('\n')

            # Write in the Project Outputs
            cmake_file.write('# Project Outputs\n')
            cmake_file.write('set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY '
                             '${CMAKE_BINARY_DIR}/lib)\n')
            cmake_file.write('set(CMAKE_LIBRARY_OUTPUT_DIRECTORY '
                             '${CMAKE_BINARY_DIR}/lib)\n')
            cmake_file.write('set(CMAKE_RUNTIME_OUTPUT_DIRECTORY '
                             '${CMAKE_BINARY_DIR}/bin)\n')
            cmake_file.write('\n')

            # Write in the Setup the project version
            cmake_file.write('# Setup the project version\n')
            cmake_file.write('set(VERSION "${HIGGS_PROJECT_VERSION}")\n')
            cmake_file.write('\n')

            # Write in the Setup the hard-coded source directory
            cmake_file.write('# Setup the hard-coded source directory\n')
            cmake_file.write('set(CMAKE_SOURCE_DIR ${HIGGS_PROJECT_SRC})\n')
            cmake_file.write('set(CMAKE_CURRENT_SOURCE_DIR '
                             '${HIGGS_PROJECT_SRC})\n')
            cmake_file.write('\n')

            # Write in the Setup External dependencies
            cmake_file.write('\n# \n')
            cmake_file.write('#\n')
            cmake_file.write('# Setup External dependencies\n')
            cmake_file.write('#\n\n')

            # Write in the includes files from the outputs directory
            cmake_file.write('# Add the include directories\n')
            cmake_file.write('set(HIGGS_EXTERNAL_INCLUDES\n')
            for include_dir in self.__get_external_deps_include_list():
                cmake_file.write('    "' + str(include_dir) + '"\n')
            cmake_file.write('    "' + str(os.path.join(
                self.__base_project_dir, self.__temp_dir,
                Utils.Constants.HIGGS_DEPS_DIR,
                'catch2', 'single_include', 'catch2')) + '"\n')
            cmake_file.write(')\n')
            cmake_file.write('\n')

            # Write in the library files from the outputs directory
            cmake_file.write('# Setup the library and linker information\n')
            cmake_file.write('set(HIGGS_EXTERNAL_LIBS\n')
            for library_file in self.__get_external_deps_linker_list():
                cmake_file.write('    "' + str(library_file) + '"\n')
            cmake_file.write(')\n')
            cmake_file.write('\n')

            # Write in the Add threading to the build process
            # TODO - Generalize to indicate whether we want to use p-threads
            cmake_file.write('# Add threading to the build process\n')
            cmake_file.write('find_package(Threads)\n')
            cmake_file.write('SET(CMAKE_CXX_FLAGS "-pthread")\n')
            cmake_file.write('\n')

            # Write in the Add/Setup llvm coverage if desired/available
            cmake_file.write('# Add/Setup llvm coverage if desired/available\n')
            cmake_file.write('SET(LLVM_COV_PATH "/usr/bin/llvm-cov")\n')
            cmake_file.write(
                'if(CMAKE_BUILD_TYPE STREQUAL "coverage" OR CODE_COVERAGE)\n')
            cmake_file.write(
                '    if("${CMAKE_C_COMPILER_ID}" MATCHES "(Apple)?[Cc]lang" OR '
                '"${CMAKE_CXX_COMPILER_ID}" MATCHES "(Apple)?[Cc]lang")\n')
            cmake_file.write(
                '        message("Building with llvm Code Coverage Tools")\n')
            cmake_file.write('\n')
            cmake_file.write('        # Warning/Error messages\n')
            cmake_file.write('        if(NOT LLVM_COV_PATH)\n')
            cmake_file.write(
                '            message(FATAL_ERROR "llvm-cov not found! '
                'Aborting.")\n')
            cmake_file.write('        endif()\n')
            cmake_file.write('\n')
            cmake_file.write('        # set Flags\n')
            cmake_file.write(
                '        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} '
                '-fprofile-instr-generate -fcoverage-mapping")\n')
            cmake_file.write(
                '        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} '
                '-fprofile-instr-generate -fcoverage-mapping")\n')
            cmake_file.write('\n')
            cmake_file.write('    elseif(CMAKE_COMPILER_IS_GNUCXX)\n')
            cmake_file.write(
                '        message("Building with lcov Code Coverage Tools")\n')
            cmake_file.write('\n')
            cmake_file.write('        # Warning/Error messages\n')
            cmake_file.write(
                '        if(NOT (CMAKE_BUILD_TYPE STREQUAL "Debug"))\n')
            cmake_file.write(
                '            message(WARNING "Code coverage results with an '
                'optimized (non-Debug) build may be misleading")\n')
            cmake_file.write('        endif()\n')
            cmake_file.write('        if(NOT LCOV_PATH)\n')
            cmake_file.write(
                '            message(FATAL_ERROR "lcov not found! '
                'Aborting...")\n')
            cmake_file.write('        endif()\n')
            cmake_file.write('        if(NOT GENHTML_PATH)\n')
            cmake_file.write(
                '            message(FATAL_ERROR "genhtml not found! '
                'Aborting...")\n')
            cmake_file.write('        endif()\n')
            cmake_file.write('\n')
            cmake_file.write(
                '        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} --coverage '
                '-fprofile-arcs -ftest-coverage")\n')
            cmake_file.write(
                '        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --coverage '
                '-fprofile-arcs -ftest-coverage")\n')
            cmake_file.write('    else()\n')
            cmake_file.write(
                '        message(FATAL_ERROR "Code coverage requires Clang or '
                'GCC. Aborting.")\n')
            cmake_file.write('    endif()\n')
            cmake_file.write('endif()\n')
            cmake_file.write('\n')

            # Write in the higgs library linker location to the R-path
            # TODO - Generalize to specify R-Path based on OS
            cmake_file.write('# Add in the higgs library linker location '
                             'to the R-path\n')
            cmake_file.write('set(CMAKE_BUILD_RPATH "/usr/lib/higgs-boson")\n')
            cmake_file.write('set(CMAKE_INSTALL_RPATH  "/usr/lib/higgs-boson")\n')
            cmake_file.write('\n')

            # Write in the Setup External dependencies
            cmake_file.write('\n# \n')
            cmake_file.write('#\n')
            cmake_file.write('# Setup Target: Main Project\n')
            cmake_file.write('#\n\n')

            # Write in the Setup the include directories for the main project
            cmake_file.write('# Setup the include directories\n')
            cmake_file.write('include_directories(${PROJECT_TARGET_MAIN} '
                             'PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_'
                             'SOURCE_DIR}/src>)\n')
            cmake_file.write('\n')

            # Write in the Setup the Headers for the main Project
            cmake_file.write('# Setup Headers\n')
            cmake_file.write('set(${PROJECT_TARGET_MAIN}_headers\n')
            for header_file in Utils.get_files_in_directory(os.path.join(
                    self.__base_project_dir, Utils.Constants.SRC_DIR),
                    Utils.Constants.HEADER_FILE_EXTENSIONS):
                cmake_file.write('        "' + str(header_file) + '"\n')
            cmake_file.write(')\n')
            cmake_file.write('\n')

            # Write in the Setup the C++ Source Files for the main Project
            cmake_file.write('# C++ Source Files\n')
            cmake_file.write('set(${PROJECT_TARGET_MAIN}_sources\n')
            for source_file in Utils.get_files_in_directory(os.path.join(
                    self.__base_project_dir, Utils.Constants.SRC_DIR),
                    Utils.Constants.SOURCE_FILE_EXTENSIONS):
                cmake_file.write('        "' + str(source_file) + '"\n')
            cmake_file.write(')\n')
            cmake_file.write('\n')

            # Write in the
            # TODO - Generalize to specify either library or executable
            cmake_file.write('# Create the actual library for main project \n')
            cmake_file.write('add_library(${PROJECT_TARGET_MAIN} SHARED '
                             '${${PROJECT_TARGET_MAIN}_sources} '
                             '${${PROJECT_TARGET_MAIN}_headers})\n')
            cmake_file.write('link_libraries(${PROJECT_TARGET_MAIN} '
                             '${HIGGS_EXTERNAL_LIBS})\n')
            cmake_file.write('\n')

            # Write in the Setup include directories for the main project
            cmake_file.write('# Setup include directories for the '
                             'main project\n')
            cmake_file.write('include_directories(${PROJECT_TARGET_MAIN} '
                             '"${HIGGS_EXTERNAL_INCLUDES}")\n')
            cmake_file.write('\n')

            # Write in the Setup External dependencies
            cmake_file.write('\n# \n')
            cmake_file.write('#\n')
            cmake_file.write('# Setup Target: Test Project\n')
            cmake_file.write('#\n\n')

            # Write in the Prepare "Catch" library for other executables
            # TODO - Fix hard-ish-coded directories
            cmake_file.write('# Prepare "Catch" library for other'
                             'executables\n')
            cmake_file.write('set(TEST_INCLUDE_DIR '
                             '${CMAKE_CURRENT_SOURCE_DIR}/test)\n')
            cmake_file.write('set(CATCH_INCLUDE_DIR '
                             '${CMAKE_CURRENT_SOURCE_DIR}'
                             '/.higgs/external/output/include/catch2)\n')
            cmake_file.write('add_library(Catch INTERFACE)\n')
            cmake_file.write('target_include_directories(Catch INTERFACE '
                             '${CATCH_INCLUDE_DIR} ${TEST_INCLUDE_DIR})\n')
            cmake_file.write('\n')

            # Write in the Setup the include directories for the test target
            cmake_file.write('# Setup the include directories for the '
                             'test target\n')
            cmake_file.write('include_directories(${PROJECT_TARGET_TEST} '
                             'PUBLIC $<BUILD_INTERFACE:'
                             '${CMAKE_CURRENT_SOURCE_DIR}/src>)\n')

            # Write in the Setup test sources
            cmake_file.write('# Setup test sources\n')
            cmake_file.write('set(TEST_SOURCES\n')
            for test_source in Utils.get_files_in_directory(os.path.join(
                    self.__base_project_dir, Utils.Constants.TEST_DIR),
                    Utils.Constants.SOURCE_FILE_EXTENSIONS
                    + Utils.Constants.HEADER_FILE_EXTENSIONS):
                cmake_file.write('        "' + str(test_source) + '"\n')
            cmake_file.write(')\n')
            cmake_file.write('\n')

            # Write in the Make the test executable
            cmake_file.write('# Make the test executable\n')
            cmake_file.write('add_executable(${PROJECT_TARGET_TEST} '
                             '${TEST_SOURCES}\n')
            cmake_file.write('        ${${PROJECT_TARGET_MAIN}_sources} '
                             '${${PROJECT_TARGET_MAIN}_headers})\n')
            cmake_file.write('\n')

            # Write in the Setup include directories for the test project
            cmake_file.write('# Setup include directories for the '
                             'test project\n')
            cmake_file.write('include_directories(${PROJECT_TARGET_TEST} '
                             '"${CMAKE_SOURCE_DIR}/src")\n')
            cmake_file.write('include_directories(${PROJECT_TARGET_TEST} '
                             '"${CMAKE_SOURCE_DIR}/test")\n')
            cmake_file.write('include_directories(${PROJECT_TARGET_TEST} '
                             '"${HIGGS_EXTERNAL_INCLUDES}")\n')
            cmake_file.write('\n')

            # Write in the Setup the test target
            cmake_file.write('# Setup the test target\n')
            cmake_file.write('link_libraries(${PROJECT_TARGET_TEST} '
                             '${HIGGS_EXTERNAL_LIBS})\n')
            cmake_file.write('link_libraries(${PROJECT_TARGET_TEST} '
                             'Catch)\n')
            cmake_file.write('\n')

            # Write in the Setup Testing definitions
            cmake_file.write('# Setup Testing definitions\n')
            cmake_file.write('target_compile_definitions(${PROJECT_TARGET_TEST}'
                             ' PRIVATE CATCH_TESTING=1)\n')
            cmake_file.write('\n')

            # Write in the Setup the LLVM Coverage Target
            cmake_file.write('# Setup the LLVM Coverage Target\n')
            cmake_file.write('add_custom_target('
                             '${PROJECT_TARGET_TEST}_coverage\n')
            cmake_file.write('        COMMAND LLVM_PROFILE_FILE='
                             '${PROJECT_TARGET_TEST}.profraw '
                             '$<TARGET_FILE:${PROJECT_TARGET_TEST}>\n')
            cmake_file.write('        COMMAND llvm-profdata merge -sparse '
                             '${PROJECT_TARGET_TEST}.profraw -o '
                             '${PROJECT_TARGET_TEST}.profdata\n')
            cmake_file.write('        COMMAND llvm-cov report '
                             '$<TARGET_FILE:${PROJECT_TARGET_TEST}> '
                             '-instr-profile=${PROJECT_TARGET_TEST}.profdata '
                             '${CMAKE_SOURCE_DIR}/src\n')
            cmake_file.write('        COMMAND llvm-cov show '
                             '$<TARGET_FILE:${PROJECT_TARGET_TEST}> '
                             '-instr-profile=${PROJECT_TARGET_TEST}.profdata '
                             '-show-line-counts-or-regions '
                             '-output-dir=${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/'
                             '${PROJECT_TARGET_TEST}-llvm-cov -format="html" '
                             '${CMAKE_SOURCE_DIR}/src\n')
            cmake_file.write('        COMMAND echo "'
                             '${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/'
                             '${PROJECT_TARGET_TEST}-llvm-cov/index.html '
                             'in your browser to view the coverage report."\n')
            cmake_file.write(')\n')
            cmake_file.write('\n')

    def run_higgs_build(self) -> bool:
        """
        Function used to build the main higgs project using its definition
        :return: Boolean indicating whether the process was successful or not
        """

        # Create a return flag
        ret_flag = False

        # Extract the relevant YAML project information
        project_yaml_info = self.__yaml_info.get_higgs_project_def()
        project_name = project_yaml_info.get_project_name().lower()
        project_version = project_yaml_info.get_project_version()

        # Setup the cache directory
        project_cache_dir = os.path.join(self.__base_project_dir,
                                         self.__temp_dir)

        # Setup the generic build path for CMake out-of-source building
        cmake_build_path = os.path.join(project_cache_dir,
                                        Utils.Constants.HIGGS_BUILD_DIR)

        # Write in the build target file and write the build steps
        build_target_path = os.path.join(project_cache_dir,
                                         Utils.Constants.HIGGS_BUILD_TARGET)
        with open(build_target_path, 'w') as target_file:

            # Write in the edit/auto-generation warning
            target_file.write('# THIS IS AN AUTOGENERATED FILE USING HIGGS\n')
            target_file.write('# DO NOT EDIT (UNLESS YOU KNOW WHAT\'S UP)\n')
            target_file.write('\n')

            # Write in the actual target definition/execution-steps
            target_file.write('cd ' + str(project_cache_dir) + str('\n'))
            target_file.write('mkdir -p ' + str(cmake_build_path) + str('\n'))
            target_file.write('cd ' + str(cmake_build_path) + str('\n'))
            target_file.write('cmake '
                              + '-DCMAKE_BUILD_TYPE=Release '
                              + '..\n')
            target_file.write('cd ..\n')
            target_file.write('cmake --build ' + str(cmake_build_path)
                              + ' --target ' + str(project_name) + '\n')
            target_file.write('\n')

        # Execute the build command in a try-catch block
        process = None
        try:
            process = subprocess.Popen(['sh', build_target_path])
            process.wait()
            ret_flag = True

        # If we hit an exception, log it
        except Exception:
            error_msg = process.stdout.read()
            Utils.tprint('\n' + str(error_msg), newline=True)

        # Return the return flag
        return ret_flag

    def run_higgs_test(self) -> bool:
        """
        Function used to test the main higgs project using its definition
        :return: Boolean indicating whether the process was successful or not
        """

        # Create a return flag
        ret_flag = False

        # Extract the relevant YAML project information
        project_yaml_info = self.__yaml_info.get_higgs_project_def()
        project_name = project_yaml_info.get_project_name().lower()
        project_version = project_yaml_info.get_project_version()

        # Setup the cache directory
        project_cache_dir = os.path.join(self.__base_project_dir,
                                         self.__temp_dir)

        # Setup the generic build path for CMake out-of-source building
        cmake_build_path = os.path.join(project_cache_dir,
                                        Utils.Constants.HIGGS_TEST_DIR)

        # Write in the test target file and write the test steps
        test_target_path = os.path.join(project_cache_dir,
                                        Utils.Constants.HIGGS_TEST_TARGET)
        with open(test_target_path, 'w') as target_file:

            # Write in the edit/auto-generation warning
            target_file.write('# THIS IS AN AUTOGENERATED FILE USING HIGGS\n')
            target_file.write('# DO NOT EDIT (UNLESS YOU KNOW WHAT\'S UP)\n')
            target_file.write('\n')

            # Write in the actual target definition/execution-steps
            target_file.write('cd ' + str(project_cache_dir) + str('\n'))
            target_file.write('mkdir -p ' + str(cmake_build_path) + str('\n'))
            target_file.write('cd ' + str(cmake_build_path) + str('\n'))
            target_file.write('cmake -DCMAKE_C_COMPILER=/usr/bin/clang '
                              + '-DCMAKE_CXX_COMPILER=/usr/bin/clang++ '
                              + '-DCMAKE_BUILD_TYPE=Debug '
                              + '..\n')
            target_file.write('cd ..\n')
            target_file.write('cmake --build ' + str(cmake_build_path)
                              + ' --target ' + str(project_name) + '_test\n')
            target_file.write('LD_LIBRARY_PATH='
                              + str(os.environ['LD_LIBRARY_PATH']) + ' '
                              + str(os.path.join(cmake_build_path, 'bin',
                                                 str(project_name) + '_test'))
                              + '\n')
            target_file.write('\n')

        # Execute the test command in a try-catch block
        process = None
        try:
            process = subprocess.Popen(['sh', test_target_path])
            process.wait()
            ret_flag = True

        # If we hit an exception, log it
        except Exception:
            error_msg = process.stdout.read()
            Utils.tprint('\n' + str(error_msg), newline=True)

        # Return the return flag
        return ret_flag

    def run_higgs_coverage(self) -> bool:
        """
        Function used to test coverage on the main higgs project using
        its definition
        :return: Boolean indicating whether the process was successful or not
        """

        # Create a return flag
        ret_flag = False

        # Extract the relevant YAML project information
        project_yaml_info = self.__yaml_info.get_higgs_project_def()
        project_name = project_yaml_info.get_project_name().lower()
        project_version = project_yaml_info.get_project_version()

        # Setup the cache directory
        project_cache_dir = os.path.join(self.__base_project_dir,
                                         self.__temp_dir)

        # Setup the generic build path for CMake out-of-source building
        cmake_build_path = os.path.join(project_cache_dir,
                                        Utils.Constants.HIGGS_COVERAGE_DIR)

        # Write in the coverage target file and write the test steps
        coverage_target_path = os.path.join(project_cache_dir,
                                            Utils.Constants.
                                            HIGGS_COVERAGE_TARGET)
        with open(coverage_target_path, 'w') as target_file:

            # Write in the edit/auto-generation warning
            target_file.write('# THIS IS AN AUTOGENERATED FILE USING HIGGS\n')
            target_file.write('# DO NOT EDIT (UNLESS YOU KNOW WHAT\'S UP)\n')
            target_file.write('\n')

            # Write in the actual target definition/execution-steps
            target_file.write('cd ' + str(project_cache_dir) + str('\n'))
            target_file.write('mkdir -p ' + str(cmake_build_path) + str('\n'))
            target_file.write('cd ' + str(cmake_build_path) + str('\n'))
            target_file.write('cmake -DCMAKE_C_COMPILER=/usr/bin/clang '
                              + '-DCMAKE_CXX_COMPILER=/usr/bin/clang++ '
                              + '-DCMAKE_BUILD_TYPE=Debug '
                              + '-DCODE_COVERAGE=ON '
                              + '..\n')
            target_file.write('cd ..\n')
            target_file.write('cmake --build ' + str(cmake_build_path)
                              + ' --target ' + str(project_name)
                              + '_test_coverage\n')
            target_file.write('\n')

        # Execute the coverage command in a try-catch block
        process = None
        try:
            process = subprocess.Popen(['sh', coverage_target_path])
            process.wait()
            ret_flag = True

        # If we hit an exception, log it
        except Exception:
            error_msg = process.stdout.read()
            Utils.tprint('\n' + str(error_msg), newline=True)

        # Return the return flag
        return ret_flag

    def __get_external_deps_linker_list(self) -> list:
        """
        Internal function used to get the list of all built libraries by
        Higgs while considering linker order specified in the YAML
        :return: List of String paths representing the libraries to link
        """

        # Deduce the output directory for the library locations
        libs_location = os.path.join(self.__base_project_dir,
                                     self.__temp_dir,
                                     Utils.Constants.HIGGS_DEPS_DIR,
                                     Utils.Constants.HIGGS_OUT_DIR,
                                     Utils.Constants.HIGGS_LIB_DIR)

        # Loop through all of the stored linker information and get the
        # highest number in the linker order value
        largest_linker_order = 0
        for linker_item_key in self.__linker_info.keys():
            linker_item = self.__linker_info[linker_item_key]
            if linker_item.get(YamlParser.YamlDefs.ORDER, 0) >\
                    largest_linker_order:
                largest_linker_order = linker_item.get(
                    YamlParser.YamlDefs.ORDER, 0)

        # Now that we have the largest linker item, increment the linker
        # order counter grabbing all ordered items as we go, effectively
        # adding the libraries in the required order
        linker_list = []
        matched_items = []
        for ii in range(-1, (largest_linker_order + 1)):
            for linker_item_key in self.__linker_info.keys():
                linker_item = self.__linker_info[linker_item_key]

                # If the current linker item matches the index value
                # then append it to the linker list
                if (linker_item.get(YamlParser.YamlDefs.ORDER, 0) <= ii) \
                        and (linker_item_key not in matched_items):

                    # List all libraries in the output directory for
                    # the matched item and add them to the return list
                    curr_lib_path = os.path.join(libs_location,
                                                 linker_item_key)
                    for lib_item in os.listdir(curr_lib_path):
                        linker_list.append(os.path.join(curr_lib_path,
                                                        lib_item))

                    # Mark that this dependency has been handled
                    matched_items.append(linker_item_key)

        # Return the list of linker items
        return linker_list

    def __get_external_deps_include_list(self) -> list:
        """
        Internal function used to get all of the includes files (from the YAML)
        for use in the main project for library reference
        :return: List of String paths representing the libraries' include files
        """

        # Create a return list
        ret_list = []

        # Start by getting the includes directory (where all root includes are)
        root_includes = os.path.join(self.__base_project_dir,
                                     self.__temp_dir,
                                     Utils.Constants.HIGGS_DEPS_DIR,
                                     Utils.Constants.HIGGS_OUT_DIR,
                                     Utils.Constants.HIGGS_INC_DIR)

        # Only continue if the root-includes directory exists
        # and the Dependency Build Manager has been setup
        if os.path.exists(root_includes):

            # Simply list the directory (non-recursively) and append the
            # resulting items to the return list
            for include_dir in os.listdir(root_includes):
                ret_list.append(os.path.join(root_includes, include_dir))

        # Return the return list
        return ret_list
