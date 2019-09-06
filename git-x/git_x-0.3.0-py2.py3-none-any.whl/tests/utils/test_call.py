import pytest
import mock
from utils import call


@mock.patch('subprocess.call', return_value=0)
def test_call(mock_call):
    command = 'ls'
    call(command)
    expected = 'ls'
    mock_call.assert_called_once_with(expected)