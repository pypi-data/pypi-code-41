# coding=utf-8

"""Put a useful module description here. """


import argparse
from yfmil3id2019 import __version__
from yfmil3id2019.ui.yfmil3id2019_test_app import run_app


def main(args=None):

    """Entry point for yfmil3id2019_test application"""

    parser = argparse.ArgumentParser(description='yfmil3id2019_test')

    ## ADD POSITIONAL ARGUMENTS
    parser.add_argument("-w", "--weights",
                        required=True,
                        type=str,
                        help="Weights")

    parser.add_argument("-n", "--network",
                        required=True,
                        type=str,
                        help="Network Architecture")

    parser.add_argument("-i", "--image",
                        required=True,
                        type=str,
                        help="Image to test")

    # ADD OPTINAL ARGUMENTS
    parser.add_argument("-o", "--output",
                        required=True,
                        type=str,
                        help="Output file"
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
        version='yfmil3id2019_test version ' + friendly_version_string)

    args = parser.parse_args(args)

    run_app(args.network, args.weights, args.image, args.output, args.verbose)
