import sys

from dinjg.core import _main


def main():
    package_name = sys.argv[1]
    return _main(package_name)
