# coding=utf-8

""" Put a useful module description here. """


import argparse
from yfmil3id2019 import __version__
from yfmil3id2019.ui.yfmil3id2019_train_app import run_app


def main(args=None):

    """Entry point for yfmil3id2019_train application"""

    parser = argparse.ArgumentParser(description='yfmil3id2019_train')

    parser.add_argument("-x",
                        required=True,
                        type=int,
                        help="1st number")

    parser.add_argument("-y",
                        required=True,
                        type=int,
                        help="2nd number")

    parser.add_argument("-m", "--multiply",
                        action="store_true",
                        help="Enable multiplication of inputs."
                        )

    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Enable verbose output",
                        )

    version_string = __version__
    friendly_version_string = version_string if version_string else 'unknown'
    parser.add_argument(
        "--version",
        action='version',
        version='yfmil3id2019_train version ' + friendly_version_string)

    args = parser.parse_args(args)

    run_app(args.x, args.y, args.multiply, args.verbose)
