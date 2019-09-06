import mock

from gitx import Gitx


@mock.patch('gitx.call', return_value=0)
def test_p(mock_call):
    Gitx().p()
    mock_call.assert_called_once_with('git pull --rebase')
