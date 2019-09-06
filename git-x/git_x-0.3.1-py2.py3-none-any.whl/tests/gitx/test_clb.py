import mock

from gitx import Gitx


@mock.patch('gitx.popen')
@mock.patch('gitx.call', return_value=0)
@mock.patch('gitx.print_confirm', return_value=True)
@mock.patch('gitx.Gitx._current_branch', return_value='master')
def test_clb_ignore_master(mock_curr_branch, mock_confirm, mock_call, mock_popen):
    mock_popen.side_effect = lambda x: '* master\n' if x == 'git branch --merged' else 0
    Gitx().clb()
    assert mock_call.call_count == 0

@mock.patch('gitx.popen')
@mock.patch('gitx.call', return_value=0)
@mock.patch('gitx.print_confirm', return_value=True)
@mock.patch('gitx.Gitx._current_branch', return_value='master')
def test_clb_branches(mock_curr_branch, mock_confirm, mock_call, mock_popen):
    mock_popen.side_effect = lambda x: 'abc\n  click\n* master\n' if x == 'git branch --merged' else 0
    Gitx().clb()
    assert mock_call.call_count == 2


@mock.patch('gitx.popen')
@mock.patch('gitx.call', return_value=0)
@mock.patch('gitx.print_confirm', return_value=True)
@mock.patch('gitx.Gitx._current_branch', return_value='abc')
def test_clb_ignore_current_branch(mock_curr_branch, mock_confirm, mock_call, mock_popen):
    mock_popen.side_effect = lambda x: 'abc\n  click\n* master\n' if x == 'git branch --merged' else 0
    Gitx().clb()
    mock_call.assert_called_once_with('git branch --delete click', exit_on_error=False)
    assert mock_call.call_count == 1


