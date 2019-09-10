import pytest
from crl.remotesession.remotesessionbase import RunResult
from crl.remotesession.exceptions import (
    SessionBackgroundExecIdAlreadyInUse,
    SessionExecIdIsNotSet)
from .utils import (
    progress_logkwargs,
    executablekwargs,
    targetkwargs,
    timeoutkwargs,
    merge_dicts,
    get_name_from_target,
    exec_idkwargs,
    get_args_from_kwargs,
    set_execute_return)


__copyright__ = 'Copyright (C) 2019, Nokia'


@progress_logkwargs()
@executablekwargs()
@targetkwargs()
@timeoutkwargs()
def test_execute_command_in_target_remoterunner(mock_remoterunner,
                                                remotesession,
                                                timeout,
                                                expected_timeout,
                                                target,
                                                expected_target,
                                                executable,
                                                expected_executable,
                                                progress_log,
                                                expected_progress_log):
    remotesession.set_runner_target(None, **get_name_from_target(target))
    execute = mock_remoterunner.return_value.execute_command_in_target
    set_execute_return(execute)
    assert remotesession.execute_command_in_target(
        'command',
        **merge_dicts(target,
                      timeout,
                      executable,
                      progress_log)) == RunResult(0, 'stdout', 'stderr')
    execute.assert_called_once_with('command',
                                    **merge_dicts(expected_timeout,
                                                  expected_target,
                                                  expected_executable,
                                                  expected_progress_log))


@targetkwargs()
@timeoutkwargs()
def test_execute_command_in_target_remotescript(mock_remotescript,
                                                remotesession,
                                                timeout,
                                                expected_timeout,
                                                target,
                                                expected_target):
    remotesession.set_target('host', 'user', 'passwd',
                             **get_name_from_target(target))
    execute = mock_remotescript.return_value.execute_command_in_target
    set_execute_return(execute)
    assert remotesession.execute_command_in_target(
        'command',
        **merge_dicts(timeout, target)) == RunResult(0, 'stdout', 'stderr')
    execute.assert_called_once_with('command', **merge_dicts(expected_timeout,
                                                             expected_target))


@exec_idkwargs()
@executablekwargs()
@targetkwargs()
@timeoutkwargs()
def test_execute_background_command_in_target_remoterunner(mock_remoterunner,
                                                           remotesession,
                                                           timeout,
                                                           expected_timeout,
                                                           target,
                                                           expected_target,
                                                           executable,
                                                           expected_executable,
                                                           exec_id,
                                                           expected_exec_id):
    remotesession.set_runner_target([{'n': 'v'}],
                                    **get_name_from_target(target))
    wait = mock_remoterunner.return_value.wait_background_execution
    set_execute_return(wait)
    remotesession.execute_background_command_in_target(
        'command', **merge_dicts(target, exec_id, executable))
    execute = (
        mock_remoterunner.return_value.execute_background_command_in_target)
    execute.assert_called_once_with('command',
                                    **merge_dicts(expected_target,
                                                  expected_exec_id,
                                                  expected_executable))
    assert remotesession.wait_background_execution(
        *get_args_from_kwargs(expected_exec_id),
        **timeout) == RunResult(0, 'stdout', 'stderr')
    wait.assert_called_once_with(*get_args_from_kwargs(expected_exec_id),
                                 **expected_timeout)


@exec_idkwargs()
@targetkwargs()
@timeoutkwargs()
def test_execute_background_command_in_target_remotescript(mock_remotescript,
                                                           remotesession,
                                                           timeout,
                                                           expected_timeout,
                                                           target,
                                                           expected_target,
                                                           exec_id,
                                                           expected_exec_id):
    remotesession.set_target('host', 'user', 'passwd',
                             **get_name_from_target(target))
    wait = mock_remotescript.return_value.wait_background_execution
    set_execute_return(wait)
    remotesession.execute_background_command_in_target(
        'command', **merge_dicts(target, exec_id))
    execute = (
        mock_remotescript.return_value.execute_background_command_in_target)
    execute.assert_called_once_with('command',
                                    **merge_dicts(expected_target,
                                                  expected_exec_id))
    assert remotesession.wait_background_execution(
        *get_args_from_kwargs(expected_exec_id), **timeout) == RunResult(
            0, 'stdout', 'stderr')
    wait.assert_called_once_with(*get_args_from_kwargs(expected_exec_id),
                                 **expected_timeout)


def test_kill_background_execution(mock_engine,
                                   remotesession):
    remotesession.execute_background_command_in_target(
        'command', target='target', exec_id='exec_id')
    remotesession.kill_background_execution('exec_id')
    mock_engine.return_value.kill_background_execution.assert_called_once_with(
        'exec_id')


def test_raises_sessionbacgroundexecidalreadyinuse(remotesession):
    remotesession.set_runner_target(None)
    with pytest.raises(SessionBackgroundExecIdAlreadyInUse) as excinfo:
        for _ in range(2):  # pragma: no branch
            remotesession.execute_background_command_in_target(
                'cmd', exec_id='exec_id')
    assert str(excinfo.value) == 'exec_id'


def test_delete_backgrounds(remotesession):
    remotesession.set_runner_target(None)
    for _ in range(2):
        remotesession.execute_background_command_in_target(
            'cmd', exec_id='exec_id')
        remotesession.wait_background_execution('exec_id')


def test_raises_sessionexecidisnotset(notsetbackground):
    with pytest.raises(SessionExecIdIsNotSet) as excinfo:
        notsetbackground.call_method()
    assert str(excinfo.value) == 'exec_id'


def test_get_source_update_env_dict(session_target, source_file, mock_engine):
    envdict = session_target.session.get_source_update_env_dict(
        source_file.source, **session_target.kwargs_to_exec)
    assert source_file.envdict == envdict
    exec_func = mock_engine.return_value.execute_command_in_target
    for _, _, kwargs in exec_func.mock_calls:
        assert kwargs['target'] == session_target.expected_target


def test_get_source_update_env_dict_raises(session_target, corrupted_source):
    with pytest.raises(corrupted_source.expected_exception) as excinfo:
        session_target.session.get_source_update_env_dict(
            corrupted_source.source, **session_target.kwargs_to_exec)

    assert corrupted_source.expected_msg in str(excinfo.value)
