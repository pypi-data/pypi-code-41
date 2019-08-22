import sys
from typing import IO, Any, List

from psyko import __version__


def main(argv: List[str] = sys.argv[1:]) -> int:
    print("Welcom to psyko {}".format(__version__))

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
