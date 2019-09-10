import pytest
from crl.remotesession.exceptions import SessionTargetIsNotSet
from .utils import (
    targetkwargs,
    protocolkwargs,
    merge_dicts,
    get_name_from_target,
    verify_target)


__copyright__ = 'Copyright (C) 2019, Nokia'


@targetkwargs()
@protocolkwargs()
def test_set_target(mock_remotescript,
                    remotesession,
                    target,
                    expected_target,
                    protocol,
                    expected_protocol):
    remotesession.set_target(
        'host', 'username', 'password',
        **merge_dicts(get_name_from_target(target),
                      protocol))
    mock_remotescript.return_value.set_target.assert_called_once_with(
        'host', 'username', 'password', **merge_dicts(
            get_name_from_target(expected_target),
            expected_protocol))
    verify_target(expected_target, mock_remotescript, remotesession)


@targetkwargs()
@protocolkwargs()
def test_set_target_with_sshkeyfile(mock_remotescript,
                                    remotesession,
                                    target,
                                    expected_target,
                                    protocol,
                                    expected_protocol):
    remotesession.set_target_with_sshkeyfile(
        'host', 'username', 'sshkeyfile',
        **merge_dicts(get_name_from_target(target),
                      protocol))
    m = mock_remotescript.return_value.set_target_with_sshkeyfile
    m.assert_called_once_with(
        'host', 'username', 'sshkeyfile',
        **merge_dicts(get_name_from_target(expected_target),
                      expected_protocol))
    verify_target(expected_target, mock_remotescript, remotesession)


def test_set_target_property(mock_remotescript,
                             remotesession):
    remotesession.set_target_property('target', 'name', 'value')
    m = mock_remotescript.return_value.set_target_property
    m.assert_called_once_with('target', 'name', 'value')
    verify_target({'target': 'target'}, mock_remotescript, remotesession)


def test_set_default_target_property(mock_remotescript,
                                     remotesession):
    remotesession.set_default_target_property('name', 'value')
    m = mock_remotescript.return_value.set_default_target_property
    m.assert_called_once_with('name', 'value')


@targetkwargs()
def test_set_runner_target(mock_remoterunner,
                           remotesession,
                           target,
                           expected_target):
    shelldicts = [{'name': 'value'}]
    remotesession.set_runner_target(
        shelldicts,
        **get_name_from_target(target))
    mock_remoterunner.return_value.set_target.assert_called_once_with(
        shelldicts, **get_name_from_target(expected_target))
    verify_target(expected_target, mock_remoterunner, remotesession)


def test_set_runner_target_property(mock_remoterunner,
                                    remotesession):
    remotesession.set_runner_target_property('target', 'name', 'value')
    m = mock_remoterunner.return_value.set_target_property
    m.assert_called_once_with('target', 'name', 'value')
    verify_target({'target': 'target'}, mock_remoterunner, remotesession)


def test_set_runner_default_target_property(mock_remoterunner,
                                            remotesession):
    remotesession.set_runner_default_target_property('name', 'value')
    m = mock_remoterunner.return_value.set_default_target_property
    m.assert_called_once_with('name', 'value')


def test_get_target_properties(mock_engine,
                               remotesession):
    assert remotesession.get_target_properties('name') == (
        mock_engine.return_value.get_target_properties.
        return_value)
    mock_engine.return_value.get_target_properties.assert_called_once_with(
        'name')


def test_get_remoterunner_targets(remotesession,
                                  mock_remoterunner):
    assert remotesession.get_remoterunner_targets() == (
        mock_remoterunner.return_value.targets)


def test_get_remotescript_targets(remotesession,
                                  mock_remotescript):
    assert remotesession.get_remotescript_targets() == (
        mock_remotescript.return_value._engine.targets)


def test_raises_sessiontargetisnotset(notsetremotesession):
    with pytest.raises(SessionTargetIsNotSet) as excinfo:
        notsetremotesession.call_method()
    assert str(excinfo.value) == 'default'


def test_env_target_creation(sessionenv):
    sessionenv.exec_and_verify()


def test_env_target_atest(atestsessionenv):
    atestsessionenv.exec_and_verify()
