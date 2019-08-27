
from os.path import exists
from json import dumps
from argparse import ArgumentParser
from gmconfig.loader import load

parser = ArgumentParser("gmconfig")

parser.add_argument('-c', '--config', help="Config location")


if __name__ == "__main__":
    args = parser.parse_args()

    if not exists(args.config):
        raise Exception("Config path doesn't exist...")

    config = load(args.config)

    print(dumps(config, indent=2, sort_keys=True))
