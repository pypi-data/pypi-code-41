import json
from .remotesessiontarget import RemoteSessionTarget
from .exceptions import (
    SessionBackgroundExecIdAlreadyInUse,
    ExecFailedError,
    SessionExecIdIsNotSet)


__copyright__ = 'Copyright (C) 2019, Nokia'


class RemoteSessionExec(RemoteSessionTarget):
    def __init__(self):
        super(RemoteSessionExec, self).__init__()
        self._backgrounds = dict()

    def execute_command_in_target(self,
                                  command,
                                  target='default',
                                  timeout=3600,
                                  executable=None,
                                  progress_log=False):
        """
        Executes remote command in the target.

        This call will block until the command has been executed.

        **Arguments:**

        *commmand*: Shell command to execute in the target
                   (example: "uname -a;ls;sleep 5;date")

        *target*:  Name of the target where to execute the command.

        *timeout*: Timeout for command in seconds.

        *executable*: The path to executable shell where the
                      command is executed.

        *progress_log*: logs progress in the level *DEBUG* if *True*.
        In practice, the *stdout* of the execution is filed line by line
        to the log.

        .. note::

            The keyword arguments *executable* and *progress_log* are not
            working in targets set by \`Set Target`\ or
            \`Set Target With Sshkeyfile\`. These arguments have no effect in
            these cases.

        *Returns:*

        Python *namedtuple* with arguments *status*, *stdout* and *stderr*.

        *Example:*

        +----------------+------------------+-----------------------+
        | ${result}=     | Execute          | echo foo; echo bar>&2 |
        |                | Command          |                       |
        |                | In Target        |                       |
        +----------------+------------------+-----------------------+
        | Should Be Equal| ${result.status} | 0                     |
        +----------------+------------------+-----------------------+
        | Should Be Equal| ${result.stdout} | foo                   |
        +----------------+------------------+-----------------------+
        | Should Be Equal| ${result.stderr} | bar                   |
        +----------------+------------------+-----------------------+

        """
        engine = self._get_engine(target)
        ekwargs = {} if engine == self._remotescript else {
            'executable': executable,
            'progress_log': progress_log}
        return self._getresult(engine.execute_command_in_target(
            command,
            target=target,
            timeout=timeout,
            **ekwargs))

    def execute_background_command_in_target(self,
                                             command,
                                             target='default',
                                             exec_id='background',
                                             executable=None):
        """
        Starts to execute remote command in the target.

        This keyword returns immediately and the command is left
        running in the background. See \`Wait Background Execution\` on
       how to read command output and \`Kill Background Execution\` on
        how to interrupt the execution.

        **Arguments:**

        *commmand*: Shell command to execute in the target
                   (example: "uname -a;ls;sleep 5;date")

        *target*:  Name of the target where to execute the command.

        *exec_id*: The execution ID of the background job.

        *executable*: The path to executable shell where the
                      command is executed.

        **Returns:**

        Nothing.

        **Example:**

        +-------------+-------------+------------------+
        | Execute     | echo Hello1;| exec_id=hello1   |
        | Background  | sleep 10    |                  |
        | Command In  |             |                  |
        | Target      |             |                  |
        +-------------+-------------+------------------+
        | Execute     | echo Hello2;| exec_id=hello2   |
        | Background  | sleep 10    |                  |
        | Command In  |             |                  |
        | Target      |             |                  |
        +-------------+-------------+------------------+
        | Kill        | hello1      |                  |
        | Background  |             |                  |
        | Execution   |             |                  |
        +-------------+-------------+------------------+
        | Kill        | hello2      |                  |
        | Background  |             |                  |
        | Execution   |             |                  |
        +-------------+-------------+------------------+
        | ${result1}= | Wait        | hello1           |
        |             | Background  |                  |
        |             | Execution   |                  |
        +-------------+-------------+------------------+
        | ${result2}= | Wait        | hello2           |
        |             | Background  |                  |
        |             | Execution   |                  |
        +-------------+-------------+------------------+

        """
        if exec_id in self._backgrounds:
            raise SessionBackgroundExecIdAlreadyInUse(exec_id)
        engine = self._get_engine(target)
        ekwargs = {} if engine == self._remotescript else {
            'executable': executable}
        engine.execute_background_command_in_target(
            command,
            target=target,
            exec_id=exec_id,
            **ekwargs)
        self._backgrounds[exec_id] = engine

    def wait_background_execution(self, exec_id, timeout=3600):
        """
        Waits for background command execution to finish.

        This keyword blocks until the background command with handle *handle*
        finishes or the timeout expires.

        **Arguments:**

        *exec_id*: The execution ID of the background job.

        *timeout*: Time to wait in seconds.

        **Returns:**

        Python *namedtuple* with arguments *status*, *stdout* and *stderr*.

        **Example:** See \`Execute Background Command In Target\`
        """
        ret = self._getresult(
            self._get_backgroundengine(exec_id).wait_background_execution(
                exec_id, timeout=timeout))
        del self._backgrounds[exec_id]
        return ret

    def kill_background_execution(self, exec_id):
        """
        Terminates the background execution.

        The command being executed is killed gracefully first with *SIGTERM*
        and, in case of failure, forcefully with *SIGKILL*.  Result is
        returned but still \`Wait Background Execution\` keyword
        returns the very same result.

        **Arguments:**

        *exec_id*: The execution ID of the background job.

        **Returns:**

        Nothing.

        *Example:* See \`Execute Background Command In Target\`
        """
        self._get_backgroundengine(exec_id).kill_background_execution(exec_id)

    def _get_backgroundengine(self, exec_id):
        return self._get_engine_for_key_from_dict(
            key=exec_id,
            enginedict=self._backgrounds,
            msg="with background exec_id '{}'".format(exec_id),
            exception=SessionExecIdIsNotSet)

    def get_source_update_env_dict(self, path, target='default'):
        """
        Get source environment updates dictionary when sourcing the *path*.
        For example if the content in *path* in *target* is::

           export VAR=VALUE

        then *{'VAR': 'VALUE'}* dictionary is returned.

        **Arguments:**

        *path*: Path to source file

        *target*: Target from where the environment is sourced

        **Returns:**

        Dictionary of updates to environment via source file.

        """
        sourced = self._get_jsonloaded(self._get_cmd_with_sourcing(path), target)
        clean = self._get_jsonloaded(self._envdict_cmd, target)
        return dict(set(sourced.items()) - set(clean.items()))

    def _get_jsonloaded(self, cmd, target):
        r = self._raise_if_failed(self.execute_command_in_target(cmd, target=target),
                                  cmd=cmd)
        return json.loads(r.stdout)

    @staticmethod
    def _raise_if_failed(result, cmd):
        if int(result.status):
            raise ExecFailedError(
                'Execution of {cmd!r} failed (status={status!r}): {msg}'.format(
                    cmd=cmd,
                    status=result.status,
                    msg=result.stderr))
        return result

    def _get_cmd_with_sourcing(self, path):
        return "{source_cmd} && {envdict_cmd}".format(
            source_cmd=self._get_source_cmd(path),
            envdict_cmd=self._envdict_cmd)

    @staticmethod
    def _get_source_cmd(path):
        return 'source {} 1>&2'.format(path)

    @property
    def _envdict_cmd(self):
        return "python -c 'import os, json; print(json.dumps(os.environ.copy()))'"
