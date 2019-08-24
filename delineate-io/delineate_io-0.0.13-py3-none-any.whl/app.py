#!/usr/bin/env python

import os
import csv
import argparse
from versions.config import Config
from versions.versions import Versions
from versions.output import JsonOutput

root_parser = argparse.ArgumentParser(description='The command line tools for https://www.delineate.io',add_help=True)
sub_parsers = root_parser.add_subparsers(dest='command')
versions = sub_parsers.add_parser('versions', help='blame people')

versions.add_argument('--out', type=str, help='Output location for the Json file')

def versions_list():
    pass

def main(command_line=None):
    """Runs the program"""

    args = root_parser.parse_args(command_line)

    if args.command == 'versions':
        
        versions = Versions(JsonOutput(args.out))

        path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(path, "versions/programs.csv")

        with open(path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter = ',')
            for row in csv_reader:
                versions.add_version(Config(row))
        
        versions.output()

if __name__ == '__main__':   # pragma: no cover
    main()