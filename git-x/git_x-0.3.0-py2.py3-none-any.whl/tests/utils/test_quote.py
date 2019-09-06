import pytest

from utils import quote


@pytest.mark.parametrize(
    "string,expected",
    [
        ('a', '"a"'),
        (None, None)
    ]
    )
def test_quote(string, expected):
    assert quote(string) == expected
