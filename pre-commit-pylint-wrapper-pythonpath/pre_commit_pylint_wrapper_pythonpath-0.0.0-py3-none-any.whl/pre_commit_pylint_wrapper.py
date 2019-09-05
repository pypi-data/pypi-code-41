import os
import sys

from pylint import run_pylint


def main():
    sys.path.insert(0, os.getcwd())
    sys.exit(run_pylint())


if __name__ == '__main__':
    main()
