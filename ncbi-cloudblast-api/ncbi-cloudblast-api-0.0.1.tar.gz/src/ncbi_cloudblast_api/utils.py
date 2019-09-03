from ._common import open_file
from pathlib import Path


def FileContents(file_path: str) -> str:
    """
    Return the contents of the file passed as input parameter

    Parameters:
    file_path (str): the path to the file of interest

    Returns:
        str: the contents of the file of interest
    """
    resolved_file_path = str(Path(file_path).resolve(strict=True))
    with open_file(resolved_file_path, 'r') as f:
        return f.read()
