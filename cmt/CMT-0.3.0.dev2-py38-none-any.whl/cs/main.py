import sys
import traceback
from argparse import ArgumentParser
from pathlib import Path

import cmt
from cmt.a_map import MapType


def main(argv=None):
    """
    Entry point into the program. Gets the arguments from the console and proceed them with :class:`~argparse.ArgumentParser`.
    Returns if its success successful 0 else 1.
    """
    if sys.version_info[0] < 3 or sys.version_info[1] < 7:
        sys.exit('Only Python 3.7 or greater is supported. You are using:' + sys.version)

    if argv is None:
        argv = sys.argv[1:]

    # TODO: find a better solution for this hard coded metadata
    parser = ArgumentParser(prog='cmt', description='Celaria Map Toolkit')
    parser.add_argument('-v', '--version', action='version', version='0.3.0.dev1')

    subparsers = parser.add_subparsers(required=True, dest='command')

    convert_parser = subparsers.add_parser('convert',
                                           help='Convert a map.')
    convert_parser.add_argument(dest='file', type=Path,
                                help='Input file.')
    convert_parser.add_argument(dest='type', type=str, choices=[t.name.lower() for t in MapType],
                                help='Map type to convert to.')
    convert_parser.add_argument(dest='version', type=int, choices=[0, 1],
                                help='Map version to convert to.')
    convert_parser.add_argument(dest='output', type=Path,
                                help='Output file.')

    args = parser.parse_args(argv)
    try:
        if args.command == 'convert':
            map_ = cmt.decode(args.file)
            new_map = cmt.convert(map_, args.version, MapType.from_str(args.type))
            cmt.encode(new_map, args.output)
    except Exception as ex:
        print('Something went wrong: ' + traceback.format_exc(ex.__traceback__))
        sys.exit(1)
    sys.exit(0)
