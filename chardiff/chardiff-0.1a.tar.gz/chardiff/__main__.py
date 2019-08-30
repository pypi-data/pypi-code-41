import argparse

import colorama

from . import chardiff, get_color


def get_args():
    parser = argparse.ArgumentParser(
        description="Compare two strings and find the diff"
    )
    parser.add_argument(
        "a", help="First string. This is the one printed to compare to."
    )
    parser.add_argument("b", help="Second string to compare to.")
    parser.add_argument("-c", "--color", help="Color to display diff", type=get_color)
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    colorama.init()
    if args.color:
        print(chardiff(args.a, args.b, marker=args.color))
    else:
        print(chardiff(args.a, args.b))
