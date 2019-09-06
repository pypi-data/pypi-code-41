import mock
from gitx import Gitx
import pytest


@mock.patch('gitx.call', return_value=0)
def test_ci(mock_call):
    Gitx().ci("comment", None, None)
    mock_call.assert_called_once_with('git commit -m "comment"')


@mock.patch('gitx.call', return_value=0)
def test_ci_exception(mock_call):
    with pytest.raises(Exception) as e:
        expected = 'Please add a valid comment.'
        Gitx().ci(None, None, None)
        assert e == expected


