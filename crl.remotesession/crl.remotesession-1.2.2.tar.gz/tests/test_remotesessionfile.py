import os
import mock
from crl.remotesession.remotesessionbase import RunResult
from .utils import (
    targetkwargs,
    timeoutkwargs,
    merge_dicts,
    destination_dirkwargs,
    modekwargs,
    new_dict_with_name,
    set_execute_return)


__copyright__ = 'Copyright (C) 2019, Nokia'


@destination_dirkwargs()
@modekwargs()
@timeoutkwargs()
def test_copy_file_between_targets_same_engine(remotesessionmocks,
                                               destination_dir,
                                               expected_destination_dir,
                                               mode,
                                               expected_mode,
                                               timeout,
                                               expected_timeout):
    copy = remotesessionmocks.engine.return_value.copy_file_between_targets
    set_execute_return(copy)

    assert remotesessionmocks.session.copy_file_between_targets(
        'target',
        'source',
        'other',
        **merge_dicts(destination_dir, mode, timeout)) == RunResult(
            0, 'stdout', 'stderr')
    copy.assert_called_once_with('target',
                                 'source',
                                 'other',
                                 **merge_dicts(expected_destination_dir,
                                               expected_mode,
                                               expected_timeout))


class Target(object):
    def __init__(self, remotesession, name, engine):
        self.remotesession = remotesession
        self.name = name
        self.engine = engine
        self.copy_from = engine.return_value.copy_file_from_target
        self.copy_to = engine.return_value.copy_file_to_target
        self._set_target()

    def _set_target(self):
        if self.name == 'script':
            self.remotesession.set_target(
                'host', 'user', 'passwd', name=self.name)
        else:
            self.remotesession.set_runner_target([{'n': 'v'}], name=self.name)
        set_execute_return(self.copy_to)


@destination_dirkwargs()
@modekwargs()
@timeoutkwargs()
def test_copy_file_between_targets_different_engine(remotemocks,
                                                    mock_shutil_rmtree,
                                                    mock_tempfile_mkdtemp,
                                                    remotesession,
                                                    destination_dir,
                                                    expected_destination_dir,
                                                    mode,
                                                    expected_mode,
                                                    timeout,
                                                    expected_timeout):
    mock_tempfile_mkdtemp.return_value = 'tmp'
    targets = (Target(remotesession, 'runner', remotemocks.runner),
               Target(remotesession, 'script', remotemocks.script))
    for source, dest in [targets, reversed(targets)]:
        assert remotesession.copy_file_between_targets(
            source.name,
            'source',
            dest.name,
            **merge_dicts(destination_dir,
                          mode,
                          timeout)) == RunResult(0, 'stdout', 'stderr')
        source.copy_from.assert_called_once_with(
            'source',
            destination='tmp',
            target=source.name,
            **expected_timeout)
        dest.copy_to.assert_called_once_with(
            os.path.join('tmp', 'source'),
            target=dest.name,
            **merge_dicts(expected_destination_dir,
                          expected_mode,
                          expected_timeout))

    assert mock_shutil_rmtree.mock_calls == [
        mock.call('tmp') for _ in range(2)]


@destination_dirkwargs()
@modekwargs()
@timeoutkwargs()
@targetkwargs()
def test_copy_directory_to_target(remotesessionmocks,
                                  destination_dir,
                                  expected_destination_dir,
                                  mode,
                                  expected_mode,
                                  timeout,
                                  expected_timeout,
                                  target,
                                  expected_target):
    copy = remotesessionmocks.engine.return_value.copy_directory_to_target
    assert remotesessionmocks.session.copy_directory_to_target(
        'source',
        **merge_dicts(
            new_dict_with_name('target_dir',
                               destination_dir),
            mode,
            timeout,
            target)) == RunResult(copy.return_value.status,
                                  copy.return_value.stdout,
                                  copy.return_value.stderr)

    copy.assert_called_once_with('source',
                                 **merge_dicts(
                                     new_dict_with_name(
                                         'target_dir',
                                         expected_destination_dir),
                                     expected_mode,
                                     expected_target,
                                     expected_timeout))


@modekwargs()
@targetkwargs()
@timeoutkwargs()
def test_create_directory_in_target(remotesessionmocks,
                                    mode,
                                    expected_mode,
                                    target,
                                    expected_target,
                                    timeout,
                                    expected_timeout):
    create = remotesessionmocks.engine.return_value.create_directory_in_target
    assert remotesessionmocks.session.create_directory_in_target(
        'path',
        **merge_dicts(mode,
                      target,
                      timeout)) == RunResult(create.return_value.status,
                                             create.return_value.stdout,
                                             create.return_value.stderr)
    create.assert_called_once_with('path',
                                   **merge_dicts(expected_mode,
                                                 expected_target,
                                                 expected_timeout))
