"""Photo Import.

A tool for importing photos from one directory into a hierarchical folder
structure in another directory based on the EXIF data of the photos.

Usage:
    photo-import [options] SOURCE DESTINATION

Arguments:
    SOURCE      photo to be imported
    DESTINATION directory to move photos into

Options:
    -h --help           Show this help.
    -m --month-only     Only create folders for months, not individual days
    -v --version        Show version.

"""
from pathlib import Path

from docopt import docopt

from photoimport import __version__
from photoimport.folders import FolderCreator, find_all_associated_files
from photoimport.photos import read_date


def main():
    """Main entry-point for the photo-import command.

    Processes all provided arguments, and performs the desired actions before
    exiting.
    """
    arguments = docopt(__doc__, version=__version__)
    creator = FolderCreator(arguments["DESTINATION"], arguments["--month-only"])

    date = read_date(Path(arguments["SOURCE"]))
    creator.create_folder(date)
    files = find_all_associated_files(Path(arguments["SOURCE"]))
    [creator.move_file(str(file), date) for file in files]
