"""
Utilities helping compare various data formats.
"""

from pathlib import PosixPath


class TextFileContentComparator:
    """
    Compare contents of two files.
    """

    def are_contents_equal(self, actual_file_path: PosixPath, expected_file_path: PosixPath) -> bool:
        """

        Args:
            actual_file_path (pathlib.PosixPath): The file path of the actual content to compare.
            expected_file_path (pathlib.PosixPath): The file path of the expected content to compare.

        Returns:
            bool: True if the contents are equal, False otherwise
        """
        actual_file_content = actual_file_path.read_text()
        expected_file_content = expected_file_path.read_text()
        return actual_file_content == expected_file_content
