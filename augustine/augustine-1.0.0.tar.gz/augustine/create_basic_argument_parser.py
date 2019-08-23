# coding=utf-8
from argparse import ArgumentParser
from typing import Any, Mapping


def create_basic_argument_parser(
        package_name=None,
        package_version=None,
        description=None,
        log_level_positional_arguments=None,
        log_level_keyword_arguments=None,
        log_file_positional_arguments=None,
        log_file_keyword_arguments=None):
    # type: (str, str, str, list, Mapping[str, Any], list, Mapping[str, Any]) -> ArgumentParser
    parser = ArgumentParser(prog=package_name, version=package_version, description=description)

    if not log_level_positional_arguments:
        log_level_positional_arguments = ['-l', '--log-level']

    if not log_level_keyword_arguments:
        log_level_keyword_arguments = dict(
            help='The log level to use for logging. Default:  INFO',
            default='INFO',
            metavar='LOGLEVEL',
            dest='log_level')

    parser.add_argument(*log_level_positional_arguments, **log_level_keyword_arguments)

    if not log_file_positional_arguments:
        log_file_positional_arguments = ['-lf', '--log-file']

    if not log_file_keyword_arguments:
        log_file_keyword_arguments = dict(
            help='The full path of the log file to use. Default:  None',
            default=None,
            metavar='LOGFILE',
            dest='log_file_path')

    parser.add_argument(*log_file_positional_arguments, **log_file_keyword_arguments)

    return parser
