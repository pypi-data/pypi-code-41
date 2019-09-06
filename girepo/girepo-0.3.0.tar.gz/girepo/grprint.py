#!/usr/bin/env python

import logging
import sys

from girepo.arg_parser import create_argparser, SubParser
from girepo.formatter import convert_as_table_format
from girepo.extractor import extract, default_mapper
from girepo.fetch import fetch_at, search
from girepo.sort import sort_by


def retrieve_data_directly(repo_full_names, mapper):
    contents = []
    for repo_full_name in repo_full_names:
        status_code, json = fetch_at(repo_full_name)
        add_retrieved_data(contents, json, mapper, status_code)

    return contents


def add_retrieved_data(contents, repo_json, mapper, status_code):
    if status_code == 200:
        content = extract(repo_json, mapper)
        contents.append(content)
    else:
        logging.error(repo_json)


def retrieve_data_heuristic(repo_names, mapper):
    contents = []
    for repo_name in repo_names:
        status_code, json = search(repo_name)
        if json.get("items"):
            add_retrieved_data(contents, json['items'][0], mapper, status_code)

    return contents


def main():
    column_names = list(default_mapper.keys())
    parser = create_argparser(sys.argv[1:], column_names)

    if parser.command_name == SubParser.STRICT.value:
        contents = retrieve_data_directly(parser.names, default_mapper)
    else:
        contents = retrieve_data_heuristic(parser.names, default_mapper)

    contents = sort_by(column_names, contents, parser)

    table_format = convert_as_table_format(column_names, contents, parser.headless)

    print(table_format)


if __name__ == '__main__':
    main()
