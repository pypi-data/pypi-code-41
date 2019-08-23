"""All the functionality to do with analysing photos

:copyright: Copyright 2019 Edward Armitage.
:license: MIT, see LICENSE for details.
"""
from datetime import datetime, date
from pathlib import Path

from exif import Image


def read_date(path: Path) -> date:
    """Reads the creation date of a photo file

    :param path: The path of the file to extract the date from
    :return: returns the date when the photo was created
    """
    with path.open(mode="rb") as image_file:
        image = Image(image_file)
        return datetime.strptime(image.datetime_original, "%Y:%m:%d %H:%M:%S").date()
