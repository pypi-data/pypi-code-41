from pathlib import PosixPath

import pytest
from expects import *

from ndd_test4p.comparators import TextFileContentComparator
from ndd_test4p.test_cases import AbstractTest


class TestTextFileContentComparator(AbstractTest):

    @pytest.fixture()
    def comparator(self) -> TextFileContentComparator:
        return TextFileContentComparator()

    @pytest.fixture()
    def actual_text_file_path(self) -> PosixPath:
        return self._test_data_file_path('actual.txt')

    def test_pass(self, comparator, actual_text_file_path):
        expected_text_file_path = self._test_data_file_path('expected-equal.txt')
        expect(comparator.are_contents_equal(actual_text_file_path, expected_text_file_path)).to(be_true)

    def test_fail_with_a_non_existent_expected_file(self, comparator, actual_text_file_path):
        expected_text_file_path = PosixPath('/non-existent.txt')
        with pytest.raises(FileNotFoundError) as error_info:
            comparator.are_contents_equal(actual_text_file_path, expected_text_file_path)
        expect(str(error_info.value)).to(contain("No such file or directory: '/non-existent.txt'"))

    def test_fail_with_a_non_existent_actual_file(self, comparator):
        actual_text_file_path = PosixPath('/non-existent.txt')
        expected_text_file_path = self._test_data_file_path('expected-equal.txt')
        with pytest.raises(FileNotFoundError) as error_info:
            comparator.are_contents_equal(actual_text_file_path, expected_text_file_path)
        expect(str(error_info.value)).to(contain("No such file or directory: '/non-existent.txt'"))

    def test_fail_with_different_content(self, comparator, actual_text_file_path):
        expected_text_file_path = self._test_data_file_path('expected-different.txt')
        expect(comparator.are_contents_equal(actual_text_file_path, expected_text_file_path)).to(be_false)
