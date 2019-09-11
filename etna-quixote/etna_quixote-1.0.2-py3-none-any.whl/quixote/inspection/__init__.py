from typing import Any, Dict, List, Union, Type
from textwrap import dedent
from contextlib import contextmanager
import subprocess

_inspection_result = {"requirements": [], "assertion_failure": None, "points": 0}


def _reset_inspection_result():
    global _inspection_result
    _inspection_result = {"requirements": [], "assertion_failure": None, "points": 0}


def get_inspection_result() -> Dict[str, Any]:
    """
    Retrieve the current inspection result

    :return:                        a dictionary describing the current inspection result
    """
    return _inspection_result


@contextmanager
def new_inspection_result(**kwargs: Any) -> Dict[str, Any]:
    """
    Create a new inspection result for the duration of a with-block

    :param kwargs:                  entries to initialize the inspection result with
    :return:                        the inspection result
    """
    try:
        global _inspection_result
        _inspection_result = {**_inspection_result, **kwargs}
        yield get_inspection_result()
    finally:
        _reset_inspection_result()


class KOError(Exception):
    """
    Exception class representing a step failure caused by the student
    """
    pass


class InternalError(Exception):
    """
    Exception class representing a step failure caused by an internal error
    """
    pass


class TimeoutError(Exception):
    """
    Exception class representing an expired timeout related error
    """

    def __init__(self, cause: Exception):
        self.__cause__ = cause

    def __str__(self):
        cmd = self.__cause__.cmd if isinstance(self.__cause__.cmd, str) else " ".join(self.__cause__.cmd)
        return dedent(f"""
        process '{cmd}' did not terminate before a timeout of {self.__cause__.timeout} seconds expired
        stdout: {self.__cause__.output}
        stderr: {self.__cause__.stderr}
        """)


class CompletedProcess:
    """
    Class representing a completed process, and providing access to its arguments, its output, and its return code
    """

    def __init__(self, completed_subprocess: subprocess.CompletedProcess):
        self.args: Union[str, List[str]] = completed_subprocess.args
        self.raw_stdout: bytes = completed_subprocess.stdout
        self.raw_stderr: bytes = completed_subprocess.stderr
        self.stdout: str = completed_subprocess.stdout.decode() if completed_subprocess.stdout is not None else None
        self.stderr: str = completed_subprocess.stderr.decode() if completed_subprocess.stderr is not None else None
        self.return_code: int = completed_subprocess.returncode

    def __bool__(self):
        return self.return_code == 0

    def __repr__(self):
        return f"CompletedProcess(\n" + \
               ",\n".join(f"    {name}={value!r}" for name, value in self.__dict__.items()) + \
               "\n)"

    def check(
            self,
            message: str,
            error_kind: Type = KOError,
            allowed_status: Union[int, List[int]] = 0,
            stdout: bool = True,
            stderr: bool = True
    ):
        """
        Check whether the execution of the process failed

        :param message:         message in case of failure to explain the reason of said failure
        :param allowed_status:  status or list of statuses that are considered successful
        :param error_kind:      exception to raise if the check failed
        :param stdout:          if True add the output of the process as a detail for the exception
        :param stderr:          if True add the error output of the process to the exception message
        """
        if isinstance(allowed_status, int):
            allowed_status = [allowed_status]
        if self.return_code not in allowed_status:
            message += f"\nexit code: {self.return_code}"
            if stdout:
                message += ("\nstdout:\n" + self.stdout) if self.stdout is not None else "\nstdout is empty"
            if stderr:
                message += ("\nstderr:\n" + self.stderr) if self.stderr is not None else "\nstderr is empty"
            raise error_kind(message)
        return self

    def expect(
            self,
            message: str,
            allowed_status: Union[int, List[int]] = 0,
            nb_points: int = 1,
            stdout: bool = True,
            stderr: bool = True
    ):
        """
        Check whether the execution of the process failed

        :param message:         message in case of failure to explain the reason of said failure
        :param allowed_status:  status or list of statuses that are considered successful
        :param nb_points:       the number of points granted by the expectation if it passes
        :param stdout:          if True add the output of the process as a detail for the exception
        :param stderr:          if True add the error output of the process to the exception message
        """
        if isinstance(allowed_status, int):
            allowed_status = [allowed_status]
        message += f"\nexit code: {self.return_code}"
        if stdout:
            message += ("\nstdout:\n" + self.stdout) if self.stdout is not None else "\nstdout is empty"
        if stderr:
            message += ("\nstderr:\n" + self.stderr) if self.stderr is not None else "\nstderr is empty"
        get_inspection_result()["requirements"].append((self.return_code in allowed_status, message, nb_points))
        return self


def _run(*args, **kwargs) -> CompletedProcess:
    """
    Run a subprocess

    This is a wrapper for subprocess.run() and all the arguments are forwarded to it
    See the documentation of subprocess.run() for the list of all the possible arguments
    :raise quixote.inspection.TimeoutError: if the timeout argument is not None and expires before the child process terminates
    """
    try:
        return CompletedProcess(subprocess.run(*args, **kwargs))
    except subprocess.TimeoutExpired as e:
        raise TimeoutError(e)
