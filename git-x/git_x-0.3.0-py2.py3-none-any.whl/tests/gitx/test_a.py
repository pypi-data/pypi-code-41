import mock
import pytest
from gitx import Gitx


@pytest.mark.parametrize(
    "include,exclude,expected_calls",
    [
        (None, None, []),
        ('a.txt', None, ['git add "a.txt"']),
        (None, 'b.txt', ['git reset "b.txt"']),
        ('a.txt', 'b.txt', ['git add "a.txt"', 'git reset "b.txt"']),
        ('a b.txt', 'b a.txt', ['git add "a b.txt"', 'git reset "b a.txt"']),
        (['a.txt', 'b.txt'], ['a.txt',  'b.txt'], ['git add "a.txt" "b.txt"', 'git reset "a.txt" "b.txt"']),
        (['a.txt b.txt'], 'a.txt b.txt', ['git add "a.txt b.txt"', 'git reset "a.txt b.txt"']),
    ]
)
def test_a(include, exclude, expected_calls):
    with mock.patch('gitx.call', return_value=0) as mock_call:
        Gitx().a(include, exclude)
        if expected_calls:
            calls = [mock.call(each) for each in expected_calls]
            print(calls)
            mock_call.assert_has_calls(calls)
        else:
            mock_call.assert_not_called()


