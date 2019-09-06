from pathlib import PosixPath

import pytest
from expects import *

from ndd_test4p.expects.content_matchers import have_same_content_as
from ndd_test4p.test_cases import AbstractTest


class TestHaveSameContentAs(AbstractTest):

    @pytest.fixture()
    def actual_text_file_path(self) -> PosixPath:
        return self._test_data_file_path('actual.txt')

    def test_pass(self, actual_text_file_path):
        expected_text_file_path = self._test_data_file_path('expected-equal.txt')
        expect(actual_text_file_path).to(have_same_content_as(expected_text_file_path))

    def test_fail_with_a_non_existent_expected_file(self, actual_text_file_path):
        expected_text_file_path = PosixPath('/non-existent.txt')
        with pytest.raises(AssertionError) as error_info:
            expect(actual_text_file_path).to(have_same_content_as(expected_text_file_path))
        expect(str(error_info.value)).to(contain(f'expected file "/non-existent.txt" does not exist'))

    def test_fail_with_a_non_existent_actual_file(self):
        actual_text_file_path = PosixPath('/non-existent.txt')
        expected_text_file_path = self._test_data_file_path('expected-equal.txt')
        with pytest.raises(AssertionError) as error_info:
            expect(actual_text_file_path).to(have_same_content_as(expected_text_file_path))
        expect(str(error_info.value)).to(contain(f'actual file "/non-existent.txt" does not exist'))

    def test_fail_with_different_content(self, actual_text_file_path):
        expected_text_file_path = self._test_data_file_path('expected-different.txt')
        with pytest.raises(AssertionError) as error_info:
            expect(actual_text_file_path).to(have_same_content_as(expected_text_file_path))
        expect(str(error_info.value)).to(contain('contents are different'))
        expect(str(error_info.value)).to(contain('useful commands:'))
        expect(str(error_info.value)).to(match(r'  diff -ru ".+/actual\.txt" ".+/expected-different\.txt"'))
        expect(str(error_info.value)).to(match(r'  meld ".+/actual\.txt" ".+/expected-different\.txt" &'))
