import argparse
from venv_clean.core.ui import run


def parse_args():
    parser = argparse.ArgumentParser(
        'venv_clean',
        description="Python Virtual Environment finder & manager")
    parser.add_argument(
        '-p', '--path', default=".",
        help='path where to look for virtual environments')
    return parser.parse_args()


def main():
    args = parse_args()
    run(args.path)


if __name__ == '__main__':
    main()
