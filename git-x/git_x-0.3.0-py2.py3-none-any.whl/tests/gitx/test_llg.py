import mock
import pytest

import utils
from gitx import Gitx


@mock.patch('gitx.call', return_value=0)
def test_llg_with_5_by_default(mock_call):
    Gitx().llg()
    expected = 'git log --oneline --pretty=format:"%C(auto)%h%Creset %C(auto)%d%Creset %s" --abbrev-commit -n {}'.format(5)
    mock_call.assert_called_once_with(expected)


@mock.patch('gitx.call', return_value=0)
def test_llg_with_graph(mock_call):
    Gitx().llg(g=True)
    expected = 'git log --graph --pretty=format:"%C(auto)%h%Creset %C(auto)%d%Creset %s" --abbrev-commit -n 5'
    mock_call.assert_called_once_with(expected)


@mock.patch('gitx.call', return_value=0)
def test_llg_with_author(mock_call):
    Gitx().llg(a=True)
    expected = 'git log --oneline --pretty=format:"%C(auto)%h%Creset %C(auto)%d%Creset %s %C(cyan)<%an>%Creset"' \
               ' --abbrev-commit -n 5'
    mock_call.assert_called_once_with(expected)


@mock.patch('gitx.call', return_value=0)
def test_llg_with_date(mock_call):
    Gitx().llg(d=True)
    expected = 'git log --oneline --pretty=format:"%C(auto)%h%Creset %C(auto)%d%Creset %s %Cgreen(%cr)%Creset"' \
               ' --abbrev-commit -n 5'
    mock_call.assert_called_once_with(expected)


@mock.patch('gitx.call', return_value=0)
def test_llg_with_all(mock_call):
    Gitx().llg(d=True, g=True, a=True, n=10)
    expected = 'git log --graph ' \
               '--pretty=format:"%C(auto)%h%Creset %C(auto)%d%Creset %s %Cgreen(%cr)%Creset %C(cyan)<%an>%Creset"' \
               ' --abbrev-commit -n 10'
    mock_call.assert_called_once_with(expected)


@mock.patch('gitx.call', return_value=0)
def test_llg_with_n(mock_call):
    n = 10
    Gitx().llg(n)
    expected = 'git log --oneline --pretty=format:"%C(auto)%h%Creset %C(auto)%d%Creset %s" --abbrev-commit -n {}'.format(n)
    mock_call.assert_called_once_with(expected)


def test_llg_with_negative():
    with pytest.raises(Exception) as e:
        n = -1
        Gitx().llg(n)
        expected = 'The commit count must be greater than zero.'
        assert e == expected
