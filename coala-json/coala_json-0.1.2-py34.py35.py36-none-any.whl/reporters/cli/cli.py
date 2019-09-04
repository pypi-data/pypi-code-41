import os
import argparse
import sys

from coala_json.reporters.ReporterFactory import ReporterFactory
from coala_json.loader.coalaJsonLoader import coalaJsonLoader
from coala_json.reporters.AppveyorReporter import AppveyorReporter


def get_path(filepath):
    return os.path.join(os.getcwd(), filepath)


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--junit', const=True, action='store_const',
                        help='mode in which coala will produce a JUnit report')
    parser.add_argument('--checkstyle', const=True, action='store_const',
                        help='mode in which coala will produce a'
                             ' Checkstyle report')
    parser.add_argument('--tap', const=True, action='store_const',
                        help='mode in which coala will produce a TAP report')
    parser.add_argument('--table', const=True, action='store_const',
                        help='mode in which coala will produce a HTML table'
                             ' report')
    parser.add_argument('--appveyor', const=True, action='store_const',
                        help='mode in which coala will upload test reports to'
                             ' appveyor')
    parser.add_argument('-f', '--input', help='path of the json input file')
    parser.add_argument('-o', '--output', help='path of output report file. '
                                               'If nothing is specified then '
                                               'coala-json will print the '
                                               'output to the stdout')
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    produce_report(parser, args)


def produce_report(parser, args):
    if not args.input:
        parser.error("Please specify a 'coala-json' input file")

    if args.appveyor:
        reporter = AppveyorReporter(coalaJsonLoader(), args.input)
        output = reporter.to_output()
    else:
        with open(get_path(args.input)) as input_file:
            factory = ReporterFactory(coalaJsonLoader(), parser, input_file,
                                      args)
            reporter = factory.get_reporter()
            output = reporter.to_output()

    if args.output:
        with open(args.output, 'w+') as report:
            report.write(output)
    else:
        sys.stdout.write(output)


if __name__ == '__main__':
    sys.exit(main())
