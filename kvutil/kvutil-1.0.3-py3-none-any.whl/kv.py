#!/usr/bin/env python

import argparse
from collections.abc import MutableMapping
import dbm
import fcntl
import io
import os
from pathlib import Path
import sys

DB_FILE_NAME = "kv"


def main():
    args = setup_arguments()
    db = setup_database(args)
    execute_and_close(args, db)


def setup_arguments():
    parser = argparse.ArgumentParser(
        description="A persistent key-value store to use with stdin/stdout."
    )
    parser.add_argument(
        "-l",
        "--list",
        help="list all 'keys'",
        dest="list",
        action="store_const",
        const=True,
        default=False,
    )
    parser.add_argument(
        "-rm",
        "--remove",
        help="delete 'key' and associated 'value'",
        dest="delete",
        action="store_const",
        const=True,
        default=False,
    )
    parser.add_argument(
        "key",
        metavar="key",
        type=str,
        help="key to uniquely identify 'value'",
        nargs="?",
        default="",
    )
    parser.add_argument(
        "value",
        metavar="value",
        type=str,
        help="data to store under 'key'",
        nargs="?",
        default=None,
    )

    return parser.parse_args()


def setup_database(args: argparse.Namespace) -> MutableMapping:
    dbfile_path = get_data_file_path()
    return open_database(dbfile_path)


def get_data_file_path() -> str:
    home = str(Path.home())
    directory = os.environ.get(
        "XDG_DATA_DIR", os.path.join(home, ".local", "share")
    )
    return os.path.join(directory, DB_FILE_NAME)


def open_database(path: str) -> MutableMapping:
    return dbm.open(path, flag="c", mode=0o600)


def execute_and_close(args: argparse.Namespace, db: MutableMapping) -> None:
    execute(args, db)
    db.close()


def execute(args: argparse.Namespace, db: MutableMapping) -> None:
    # setup database lock
    lockfile_path = ".".join([get_data_file_path(), "lock"])
    lockfile = open(lockfile_path, "w+")

    # execute statement
    if args.list:
        execute_list(db, lockfile)
    elif args.delete:
        execute_delete(db, args.key, lockfile)
    elif args.value:
        execute_write(db, args.key, args.value, lockfile)
    else:
        execute_read(db, args.key, lockfile)

    # unlock database
    fcntl.lockf(lockfile, fcntl.LOCK_UN)
    lockfile.close()


def execute_list(db: MutableMapping, lockfile: io.TextIOWrapper) -> None:
    fcntl.lockf(lockfile, fcntl.LOCK_SH)
    for key in db.keys():
        print(key.decode("utf8"), file=sys.stdout)


def execute_delete(db: MutableMapping, key: str, lockfile: io.TextIOWrapper) -> None:
    fcntl.lockf(lockfile, fcntl.LOCK_EX)
    try:
        del db[key]
    except KeyError:
        pass  # key already not in database!


def execute_write(
    db: MutableMapping, key: str, value: str, lockfile: io.TextIOWrapper
) -> None:
    fcntl.lockf(lockfile, fcntl.LOCK_EX)
    db[key] = value


def execute_read(db: MutableMapping, key: str, lockfile: io.TextIOWrapper) -> None:
    fcntl.lockf(lockfile, fcntl.LOCK_SH)
    try:
        print(db[key].decode("utf8"), file=sys.stdout)
    except KeyError:
        pass  # print nothing


if __name__ == "__main__":
    main()
