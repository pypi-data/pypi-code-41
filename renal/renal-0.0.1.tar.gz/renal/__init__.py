# Copyright (c) 2019 Xiaoyong Guo

import pathlib
import string
import sys


def rename(from_path, to_path):
    if not from_path.exists():
        print('File does not exist: %s', filepath)
        return False
    elif to_path.exists():
        print("%s already exists - skipping..." % to_path)
        return False
    else:
        from_path.rename(to_path)
        print("renamed %s to %s" % (from_path, to_path))
        return True


def convert_path(from_path):
    name = from_path.name.lower()
    allowable = '.' + string.ascii_lowercase + string.digits + string.whitespace
    new_name = ''.join(c for c in name if c in allowable).split()
    new_name = '_'.join(new_name)
    to_path = from_path.parent.joinpath(new_name)
    return to_path


def main(args=None):
    args = args or sys.argv
    if len(args) < 2:
      print('Need one filepath.')
      return

    from_path = pathlib.Path(args[1])
    to_path = convert_path(from_path)
    rename(from_path, to_path)


if __name__ == '__main__':
    main(sys.argv)
