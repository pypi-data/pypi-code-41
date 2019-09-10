import pytest


__copyright__ = 'Copyright (C) 2019, Nokia'


def targetkwargs():
    return pytest.mark.parametrize('target, expected_target', [
        ({}, {'target': 'default'}),
        ({'target': 'target'}, {'target': 'target'})])


def timeoutkwargs():
    return pytest.mark.parametrize('timeout, expected_timeout', [
        ({}, {'timeout': 3600}),
        ({'timeout': 10}, {'timeout': 10})])


def executablekwargs():
    return pytest.mark.parametrize('executable, expected_executable', [
        ({}, {'executable': None}),
        ({'executable': 'executable'}, {'executable': 'executable'})])


def progress_logkwargs():
    return pytest.mark.parametrize('progress_log, expected_progress_log', [
        ({}, {'progress_log': False}),
        ({'progress_log': True}, {'progress_log': True})])


def exec_idkwargs():
    return pytest.mark.parametrize('exec_id, expected_exec_id', [
        ({}, {'exec_id': 'background'}),
        ({'exec_id': 'exec_id'}, {'exec_id': 'exec_id'})])


def protocolkwargs():
    return pytest.mark.parametrize('protocol, expected_protocol', [
        ({}, {'protocol': 'ssh/sftp'}),
        ({'protocol': 'protocol'}, {'protocol': 'protocol'})])


def destination_dirkwargs():
    return pytest.mark.parametrize(
        'destination_dir, expected_destination_dir', [
            ({}, {'destination_dir': '.'}),
            ({'destination_dir': 'destination_dir'},
             {'destination_dir': 'destination_dir'})])


def modekwargs():
    return pytest.mark.parametrize('mode, expected_mode', [
        ({}, {'mode': '0755'}),
        ({'mode': 'mode'}, {'mode': 'mode'})])


def merge_dicts(*args):
    ret = dict()
    for a in args:
        ret.update(a)
    return ret


def new_dict_with_name(name, target):
    ret = dict()
    for _, v in target.items():
        ret[name] = v
    return ret


def get_name_from_target(target):
    return new_dict_with_name('name', target)


def get_args_from_kwargs(kwargs):
    return [v for _, v in kwargs.items()]


def verify_target(target, mock_engine, remotesession):
    remotesession.copy_file_from_target('source', **target)
    m = mock_engine.return_value.copy_file_from_target
    m.assert_called_once_with('source',
                              destination=None,
                              timeout=3600,
                              **target)


def set_execute_return(execute):
    execute.return_value.status = 0
    execute.return_value.stdout = 'stdout'
    execute.return_value.stderr = 'stderr'
