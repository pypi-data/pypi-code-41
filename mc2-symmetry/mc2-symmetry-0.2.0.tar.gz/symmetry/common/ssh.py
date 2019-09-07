import logging
import os
import threading
import time
from abc import ABC
from concurrent.futures import ThreadPoolExecutor
from typing import List

from paramiko import AutoAddPolicy, Channel
from paramiko.client import SSHClient
from paramiko.ssh_exception import NoValidConnectionsError

logger = logging.getLogger(__name__)


class Result:

    def __init__(self, connection, stdout=None, stderr=None, error=None) -> None:
        super().__init__()
        self.stdout = stdout.readlines() if stdout else None
        self.stderr = stderr.readlines() if stderr else None
        self.error = error
        self.connection = connection

    @property
    def result(self):
        if self.failed:
            return self.error

        out = os.linesep.join([line.strip() for line in self.stdout])
        err = os.linesep.join([line.strip() for line in self.stderr])

        if err:
            return out + os.linesep + err
        else:
            return out

    @property
    def failed(self):
        return self.error is not None

    def __str__(self) -> str:
        return 'Result(failed=%s, result=%s)' % (self.failed, self.result)


class ExecutionException(Exception):

    def __init__(self, result: Result, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.result = result


class Connection:

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self.ssh = SSHClient()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        self.args = args
        self.kwargs = kwargs
        self._connected = False
        self.connect_lock = threading.Lock()
        self._sftp = None

    def channel(self) -> Channel:
        self.ensure_connection()
        return self.ssh.get_transport().open_session()

    def run(self, *args, **kwargs) -> Result:
        self.ensure_connection()

        try:
            _, stdout, stderr = self.ssh.exec_command(*args, **kwargs)
            return Result(self, stdout, stderr)
        except Exception as e:
            raise ExecutionException(Result(self, error=e))

    @property
    def is_connected(self):
        self.connect_lock.acquire()
        try:
            return self._connected
        finally:
            self.connect_lock.release()

    def disconnect(self):
        self.connect_lock.acquire()
        try:
            if not self._connected:
                return False

            self.ssh.close()
            return True
        finally:
            self._connected = False
            self.connect_lock.release()

    def ensure_connection(self):
        if not self._connected:
            self.connect()

    def connect(self):
        with self.connect_lock:
            if self._connected:
                return

            logger.debug("Initializing ssh connection from thread %s to %s", threading.current_thread().getName(), self)
            try:
                self.ssh.connect(*self.args, **self.kwargs)
                logger.info('SSH connection established successfully %s', self)
            except Exception as e:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.exception('Error while initializing ssh connection %s', self)
                else:
                    logger.info('Error while initializing ssh connection %s: %s', self, e)
                raise e

            self._connected = True

    def close(self):
        self._connected = False
        self.ssh.close()

    def open_sftp(self):
        if not self._sftp:
            self._sftp = self.ssh.open_sftp()
            self._sftp.ssh_client = self.ssh

    def change_sftp_dir(self, path=None):
        if self._sftp:
            self._sftp.chdir(path)

    def get_sftp_file(self, file, mode='r'):
        if self._sftp:
            return self._sftp.file(file, mode)
        else:
            return None

    def __str__(self):
        return 'Connection(%s, %s)' % (self.args, self.kwargs)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return self


class GroupResult(dict):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._succeeded = None
        self._failed = None

    def _bifurcate(self):
        self._succeeded = dict()
        self._failed = dict()

        for c, r in self.items():
            if r.failed:
                self._failed[c] = r
            else:
                self._succeeded[c] = r

    @property
    def succeeded(self):
        if self._succeeded is None:
            self._bifurcate()

        return self._succeeded

    @property
    def failed(self):
        if self._failed is None:
            self._bifurcate()

        return self._failed


class GroupExecutionException(Exception):

    def __init__(self, result: GroupResult, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.result = result


class ConnectionGroup:

    def __init__(self, connections: List[Connection]) -> None:
        super().__init__()
        self.connections = connections

    def run(self, *args, **kwargs) -> GroupResult:
        raise NotImplementedError()

    def disconnect(self):
        for c in self.connections:
            c.disconnect()

    def close(self):
        for c in self.connections:
            c.close()


class SerialConnectionGroup(ConnectionGroup):

    def run(self, *args, **kwargs) -> GroupResult:
        results = GroupResult()

        err = False

        for c in self.connections:
            try:
                result = c.run(*args, **kwargs)
            except ExecutionException as e:
                err = True
                result = e.result
            except Exception as e:
                err = True
                result = Result(c, error=e)

            results[c] = result

        if err:
            raise GroupExecutionException(results)

        return results


class ThreadedConnectionGroup(ConnectionGroup):

    def __init__(self, connections: List[Connection], max_workers=None) -> None:
        super().__init__(connections)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def shutdown(self):
        self.executor.shutdown()

    def run(self, *args, **kwargs) -> GroupResult:
        futures = dict()

        for c in self.connections:
            futures[c] = self.executor.submit(c.run, *args, **kwargs)

        results = GroupResult()

        err = False

        for c, ftr in futures.items():
            try:
                result = ftr.result()
            except ExecutionException as e:
                err = True
                result = e.result
            except Exception as e:
                err = True
                result = Result(c, error=e)

            results[c] = result

        if err:
            raise GroupExecutionException(results)

        return results


class Command:

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self.args = args
        self.kwargs = kwargs

    def run(self, connection):
        return connection.run(*self.args, **self.kwargs)


class StopAgentException(Exception):
    pass


class AgentListener(ABC):
    def on_result(self, connection: Connection, command: Command, result: Result):
        raise NotImplementedError()

    def on_exception(self, connection: Connection, command: Command, exception):
        pass


class Agent:

    def __init__(self, connection: Connection, command: Command, listener: AgentListener, interval, timeout,
                 retry=5) -> None:
        super().__init__()
        self.connection = connection
        self.command = command
        self.listener = listener
        self.interval = interval
        self.timeout = timeout
        self.retry = retry

        self.connection.kwargs['timeout'] = timeout
        self.command.kwargs['timeout'] = timeout

        self._cancelled = False

    def run(self):
        c = self.connection
        cmd = self.command
        listener = self.listener

        try:
            next_time = time.time()

            while not self._cancelled:
                next_time += self.interval

                try:
                    c.ensure_connection()

                    result = cmd.run(c)
                    listener.on_result(c, cmd, result)

                    time.sleep(max(0, next_time - time.time()))

                except ExecutionException as e:
                    c.disconnect()
                    result = e.result
                    listener.on_result(c, cmd, result)
                    time.sleep(self.retry)
                    next_time = time.time()
                    continue

                except NoValidConnectionsError as e:
                    listener.on_result(c, cmd, Result(c, error=e))
                    time.sleep(self.retry)
                    next_time = time.time()
                    continue

                except StopAgentException:
                    break

                except Exception as e:
                    c.disconnect()
                    listener.on_exception(c, cmd, e)
                    time.sleep(self.retry)
                    next_time = time.time()
                    continue

        except StopAgentException:
            pass

    def cancel(self):
        self._cancelled = True
