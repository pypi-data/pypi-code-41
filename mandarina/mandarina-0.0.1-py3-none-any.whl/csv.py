"""
This module provides functions to work with various files
"""

import subprocess
import os


def day_is_already_written(todays_date, filename):
    """
    Checks if the specified date is already written to a csv or textfile.

    :param todays_date: Date as string like "2018-01-01"
    :param filename: Filename to check
    :return: True if Date is present in the last line of the file
    """
    line = subprocess.check_output(["tail", "-1", filename])
    last_line = line.decode("utf-8")
    return todays_date in last_line


def delete_last_line(filename):
    """
    Deletes the last line of the specified file.
    :param filename: Filename to delete the last line from
    :return: None
    """
    with open(filename, "r+", encoding="utf-8") as file:
        # Move the pointer (similar to a cursor in a text editor) to the end of the file
        file.seek(0, os.SEEK_END)
        # This code means the following code skips the very last character in the file -
        # i.e. in the case the last line is null we delete the last line
        # and the penultimate one
        pos = file.tell() - 1
        # Read each character in the file one at a time from the penultimate
        # character going backwards, searching for a newline character
        # If we find a new line, exit the search
        while pos > 0 and file.read(1) != "\n":
            pos -= 1
            file.seek(pos, os.SEEK_SET)
        # So long as we're not at the start of the file, delete all the characters ahead
        # of this position
        if pos > 0:
            file.seek(pos, os.SEEK_SET)
            file.truncate()


def create_headers(filename, header_row):
    """
    Creates a csv header row if the specified file is empty
    or doesn't exist.

    :param filename: The path of the file
    :param header_row: String for the header row
    :return True if file was empty and header is written
    """
    with open(filename, "a") as file:
        if os.stat(filename).st_size == 0:
            file.write(header_row + "\n")
            return True
        return False
