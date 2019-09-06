"""
Content matchers for the `expects <https://expects.readthedocs.io/en/stable/>`_ library.
"""

from pathlib import PosixPath

from expects.matchers import Matcher

from ndd_test4p.comparators import TextFileContentComparator


class have_same_content_as(Matcher):  # pylint: disable=invalid-name
    """
    Check that a file has the same content as another one.

    :Examples:

    .. code-block:: python

        expect(actual_text_file_path).to(have_same_content_as(expected_text_file_path))
    """

    def __init__(self, expected_file_path: PosixPath):
        """
        Args:
            expected_file_path (PosixPath): The file path of the expected content to compare.
        """
        self._expected = expected_file_path
        self._expected_file_path = expected_file_path

    def _match(self, subject):
        """
        Args:
            subject (PosixPath): The file path of the actual content to compare.

        Returns:
            (bool, [str]): The result of the comparison and its associated message.
        """
        actual_file_path = subject

        if not self._expected_file_path.is_file():
            return False, [f'expected file "{self._expected_file_path.as_posix()}" does not exist']

        if not actual_file_path.is_file():
            return False, [f'actual file "{actual_file_path.as_posix()}" does not exist']

        if TextFileContentComparator().are_contents_equal(actual_file_path, self._expected_file_path):
            return True, ['contents are equals']

        return False, [
            'contents are different\n'
            + 'useful commands:\n'
            + f'  diff -ru "{actual_file_path}" "{self._expected_file_path}"\n'
            + f'  meld "{actual_file_path}" "{self._expected_file_path}" &'
        ]
