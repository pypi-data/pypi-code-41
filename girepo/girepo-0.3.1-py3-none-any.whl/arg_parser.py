#!/usr/bin/env python

import re
import argparse

from enum import Enum


class SubParser(Enum):
    STRICT = "strict"
    ST = "st"
    ROUGH = "rough"
    RO = "ro"


def is_strict_command(parser):
    return parser.command_name == SubParser.STRICT.value or parser.command_name == SubParser.ST.value


def is_rough_command(parser):
    return parser.command_name == SubParser.ROUGH.value or parser.command_name == SubParser.RO.value


def full_name_type(value, pattern=re.compile(r"^(( )*[\w\.\-]+( )*/( )*[\w\.\-]+( )*)$")):
    """
    allow the value contains white-space at around words

    https://regex101.com/r/ks59iR/4

    :param value:
    :param pattern:
    :return:
    """
    if not pattern.match(value):
        raise argparse.ArgumentTypeError("the format of name should be like owner/repo")
    return value.replace(' ', '')


def create_argparser(args, sort_keys):
    parser = argparse.ArgumentParser(
        description="""
        Print Git Repositories information with the markdown format for your documents.
        
        This uses github api without authentication. 
        So you could reach the rate-limitation if you use this 60 requests per hour.
        https://developer.github.com/v3/#rate-limiting
        
        Could you take a cup of coffee \U00002615 until recovering if you exceed. 
        """,
        epilog="God bless you.",
        fromfile_prefix_chars="@"
    )

    subparsers = parser.add_subparsers(
        title='subcommands',
        description="you can choose a search way from sub-commands.\
         rough sub-command does not require owner info but it might return wrong info.",
        dest='command_name',
    )

    # rough
    subparser_heuristic = subparsers.add_parser(SubParser.ROUGH.value,
                                                description="This is a heuristic search.\
                                                 This is possible to return the wrong repository info.",
                                                aliases=[SubParser.RO.value],
                                                help='heuristic search. see `girepo ro --help`')
    subparser_heuristic.add_argument('names', nargs='+',
                                     help='the target repositories')
    add_options(subparser_heuristic, sort_keys)

    # strict
    subparser_strict = subparsers.add_parser(SubParser.STRICT.value,
                                             description="This is a strict search.\
                                               This requires owner and repository name as \"onwer/repository\".",
                                             aliases=[SubParser.ST.value], help='strict search. see `girepo st --help`')
    subparser_strict.add_argument('names', type=full_name_type, nargs='+',
                                  help='the target repositories written like owner/repository')
    add_options(subparser_strict, sort_keys)

    return parser.parse_args(args)


def add_options(parser, sort_keys):
    parser.add_argument('--headless', dest="headless", action='store_true',
                        help='not to describe table headers')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-a', '--asc', dest="asc_key", choices=sort_keys,
                       help='sort by asc with the field')
    group.add_argument('-d', '--desc', dest="desc_key", choices=sort_keys,
                       help='sort by desc with the field')
