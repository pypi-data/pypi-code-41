import mock

from gitx import Gitx


@mock.patch('gitx.call', return_value=0)
def test_co(mock_call):
    Gitx().co("master")
    mock_call.assert_called_once_with('git checkout master')


@mock.patch('gitx.call', return_value=0)
def test_co_create_if_not_exist(mock_call):
    Gitx().co("master", create_if_not_existed=True)
    mock_call.assert_called_once_with('git checkout -b master')


@mock.patch('gitx.call', return_value=0)
def test_co_create_if_not_exist_with_start_point(mock_call):
    Gitx().co("master", 'c1ff877', create_if_not_existed=True)
    mock_call.assert_called_once_with('git checkout -b master c1ff877')


@mock.patch('gitx.call', return_value=0)
def test_co_ignore_start_point_if_not_create_new(mock_call):
    Gitx().co("master", 'c1ff877', create_if_not_existed=False)
    mock_call.assert_called_once_with('git checkout master')


@mock.patch('gitx.popen')
@mock.patch('gitx.call', return_value=0)
def test_co_with_partial_branch_name_but_unique(mock_call, mock_popen):
    mock_popen.side_effect = lambda x: 'abc\n  click\n* master\n' if x == 'git branch' else 0
    Gitx().co("ma")
    mock_call.assert_called_once_with('git checkout master')


@mock.patch('gitx.print_prompt', return_value=1)
@mock.patch('gitx.popen')
@mock.patch('gitx.call', return_value=0)
def test_co_with_partial_branch_name_but_not_unique(mock_call, mock_popen, _):
    mock_popen.side_effect = lambda x: 'abc\n  click\n* master\n' if x == 'git branch' else 0
    Gitx().co("a")
    mock_call.assert_called_once_with('git checkout master')
