"""Utility functions for internal use."""

import os
import sys


def find_executable(basename, search_dirs=None):
    """Find the specified executable.

    The suffix ".exe" will automatically be appended to the basename
    on Microsoft Windows systems.

    If no search_dirs are specified, the default is to search all
    directories in the system's $PATH.

    Returns the full path to the executable if found, None otherwise.
    """

    # Ensure this is, in fact, a basename
    basename = os.path.basename(basename)

    # Append a file suffix if necessary
    if sys.platform.startswith("win"):
        basename += ".exe"

    if not search_dirs:
        # Search the system $PATH
        search_dirs = os.getenv("PATH").split(os.pathsep)

    for search_dir in search_dirs:
        candidate = os.path.join(search_dir, basename)
        if os.path.exists(candidate):
            return candidate
