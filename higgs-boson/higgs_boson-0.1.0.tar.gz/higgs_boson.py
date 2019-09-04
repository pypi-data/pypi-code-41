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

import argparse
from builder import Commands


def build_parser():
    """
    Function used to build-up the argument parser for all of the supported CLI
    sub-commands and corresponding arguments for the CLI tool
    :return: Python Argument Parser representing the parsed arguments
    """

    # Setup the main argument parser instance
    parser = argparse.ArgumentParser(prog='higgs-boson',
                                     epilog='(C) BitBoson')

    # Add in the common arguments
    parser.add_argument('-d', '--directory', dest='project_dir',
                        type=str, help='Directory to initialize on.')
    parser.add_argument('-c', '--cache', dest='cache_dir',
                        type=str, help='Directory to use as the cache (name).')
    parser.add_argument('-f', '--file', dest='higgs_file',
                        type=str, help='Higgs Configuration File (name).')
    parser.add_argument('-D', '--Docker', dest='use_docker',
                        action='store_true',
                        help='Flag indicating whether to use Docker or not')

    # Create the sub-parser
    sub_parsers = parser.add_subparsers(help='sub-command help')
    sub_parsers.required = True
    sub_parsers.dest = 'command'

    # Add in the sub-commands for the higgs builder
    sub_parsers.add_parser('init', help='init help', epilog='(C) BitBoson')
    deps_sub_parser = sub_parsers.add_parser('deps', help='deps help',
                                             epilog='(C) BitBoson')
    build_sub_parser = sub_parsers.add_parser('build', help='build help',
                                              epilog='(C) BitBoson')
    sub_parsers.add_parser('test', help='test help', epilog='(C) BitBoson')
    sub_parsers.add_parser('coverage', help='coverage help',
                           epilog='(C) BitBoson')

    # Add in the arguments for the deps parser
    deps_sub_parser.add_argument('-o', '--os', dest='build_os',
                                 type=str, help='Targeted OS for Build.')
    deps_sub_parser.add_argument('-a', '--arch', dest='build_arch',
                                 type=str, help='Targeted Arch. for Build.')

    # Add in the arguments for the build parser
    build_sub_parser.add_argument('-o', '--os', dest='build_os',
                                  type=str, help='Targeted OS for Build.')
    build_sub_parser.add_argument('-a', '--arch', dest='build_arch',
                                  type=str, help='Targeted Arch. for Build.')

    # Return the parser for further use
    return parser.parse_args()


def main() -> None:
    """
    Main function for the Python module (for use with CLI)
    :return: None
    """

    # build parser
    parser = build_parser()

    # Handle the init sub-command
    if parser.command == 'init':
        Commands.handle_init_command(project_dir=parser.project_dir,
                                     cache_dir=parser.cache_dir)

    # Handle the deps sub-command
    if parser.command == 'deps':
        Commands.handle_deps_command(project_dir=parser.project_dir,
                                     higgs_file=parser.higgs_file,
                                     cache_dir=parser.cache_dir,
                                     use_docker=parser.use_docker,
                                     build_os=parser.build_os,
                                     build_arch=parser.build_arch)

    # Handle the build sub-command
    if parser.command == 'build':
        Commands.handle_build_command(project_dir=parser.project_dir,
                                      higgs_file=parser.higgs_file,
                                      cache_dir=parser.cache_dir,
                                      use_docker=parser.use_docker,
                                      build_os=parser.build_os,
                                      build_arch=parser.build_arch)

    # Handle the test sub-command
    if parser.command == 'test':
        Commands.handle_test_command(project_dir=parser.project_dir,
                                     higgs_file=parser.higgs_file,
                                     cache_dir=parser.cache_dir,
                                     use_docker=parser.use_docker)

    # Handle the coverage sub-command
    if parser.command == 'coverage':
        Commands.handle_coverage_command(project_dir=parser.project_dir,
                                         higgs_file=parser.higgs_file,
                                         cache_dir=parser.cache_dir,
                                         use_docker=parser.use_docker)


# Implement main function for use with CLI
if __name__ == "__main__":
    main()
