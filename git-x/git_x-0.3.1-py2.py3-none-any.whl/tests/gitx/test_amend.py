import mock
from gitx import Gitx


@mock.patch('gitx.call', return_value=0)
@mock.patch('gitx.Gitx.a', return_value=0)
def test_amend(mock_a, mock_call):
    Gitx().amend('a.txt', 'a.txt', False)
    mock_a.assert_called_once_with('a.txt', 'a.txt')
    mock_call.assert_called_once_with('git commit --amend --no-edit')

@mock.patch('gitx.call', return_value=0)
@mock.patch('gitx.Gitx.a', return_value=0)
def test_amend_no_edit(mock_a, mock_call):
    Gitx().amend('a.txt', 'a.txt', True)
    mock_a.assert_called_once_with('a.txt', 'a.txt')
    mock_call.assert_called_once_with('git commit --amend')




