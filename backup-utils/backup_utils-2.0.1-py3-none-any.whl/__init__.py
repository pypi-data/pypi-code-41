import argparse
from .Backup import Backup

__all__ = ["Backup", "main"]
__version__ = "2.0.1"
__author__ = "Oprax <oprax@me.com>"


def main():
    """
    Expose `backup_utils` method as a command line.
    """
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "-v", "--version", action="version", version="{}".format(__version__)
    )
    parser.add_argument(
        "-r",
        "--run",
        action="store_true",
        help="Create a new backup, default command if no args has given",
    )
    parser.add_argument(
        "-n",
        "--notify",
        action="store_true",
        help="Send a notification to test notifier settings",
    )
    parser.add_argument(
        "-c",
        "--config",
        action="store_true",
        help="Display path of the settings file",
    )
    parser.add_argument(
        "-d",
        "--dir",
        required=False,
        action="append",
        help="Add a new directory to the backup list, so next run it will be back up",
    )
    args = parser.parse_args()
    bak = Backup()
    if args.dir:
        bak.add_dir(args.dir)
    elif args.config:
        bak.config()
    elif args.notify:
        bak.notify(
            "Hi, your notifier settings is working !",
            attachments={"test.log": b"test data"},
        )
    else:
        bak.run()
