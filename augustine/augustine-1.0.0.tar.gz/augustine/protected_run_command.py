# coding=utf-8
from os import environ, linesep, sep
from gevent import monkey, spawn
from gevent.fileobject import FileObject
from gevent.subprocess import Popen, PIPE
from sys import stderr, stdout
from typing import Dict, Iterable, Union

from .environment_overlay import EnvironmentOverlay
from ._core import log


monkey.patch_all(sys=True)


def _synchronize_stream(in_stream, out_stream, output=None, show_output=None):
    if show_output is None:
        show_output = True

    try:
        in_file = FileObject(in_stream)
        for line in in_file:
            if show_output:
                out_stream.write(line)

            if output is not None:
                output.append(line.rstrip())

    except BaseException as exception:
        log.error("Error while reading stream {}: {}".format(repr(in_stream), repr(exception)))


def run_command(
        command=None,
        arguments=None,
        working_directory=None,
        standard_output=None,
        error_output=None,
        show_output=None,
        raise_exceptions=None,
        environment_overlay=None):
    # type: (str, Iterable[str], str, [], [], bool, bool, EnvironmentOverlay) -> int
    if show_output is None:
        show_output = True

    if raise_exceptions is None:
        raise_exceptions = True

    if arguments is None:
        arguments = list()

    if command:
        arguments.insert(0, command)

    if not arguments:
        raise ValueError('In order to run a command, a command, arguments, or both must be specified.')

    log.debug(
        "Invoking: {1}{0}"
        "\tCapture stdout?: {2}\tCapture stderr?: {3}\tShow output?: {4}\tRaise exceptions: {5}{0}"
        "\tWorking directory: {6}{0}"
        "\tEnvironment overlay: {7}{0}".format(
            linesep,
            ' '.join(arguments),
            standard_output is not None,
            error_output is not None,
            show_output,
            raise_exceptions,
            working_directory,
            repr(environment_overlay)))

    environment = None if not environment_overlay else environment_overlay.overlay(environ)

    process = Popen(
        args=arguments,
        cwd=working_directory,
        stdout=PIPE,
        stderr=PIPE,
        env=environment)

    stdout_routine = spawn(_synchronize_stream, process.stdout, stdout, standard_output, show_output)
    stderr_routine = spawn(_synchronize_stream, process.stderr, stderr, error_output, show_output)

    stdout_routine.join()
    stderr_routine.join()
    exit_code = process.wait()

    log.debug('Exit code: ' + str(exit_code))

    if exit_code != 0:
        message = str(
            "Non-zero exit detected from sub-process:{0}"
            "\tArguments: {1}{0}"
            "\tExit code: {2}{0}"
            "\tWorking directory: {3}{0}".format(
                linesep,
                ' '.join(arguments),
                str(exit_code),
                repr(working_directory)))
        if raise_exceptions:
            log.debug('raising exception: ' + message)
            process.stderr.close()
            process.stdout.close()
            raise RuntimeError(message)

        log.error(message)

    return exit_code


def _find_environment(merge_environment=None, overwrite_environment=None):
    # type: (Dict[str, str], Dict[str, str]) -> Union[Dict[str, str], None]
    if not merge_environment and not overwrite_environment:
        return None

    environment = environ.copy()
    environment = _merge_environment(environment, merge_environment)
    environment = _overwrite_environment(environment, overwrite_environment)

    return environment


def _merge_environment(environment, merge_environment):
    # type: (Dict[str, str], Dict[str, str]) -> Dict[str, str]
    if not merge_environment:
        return environment

    merged_environment = dict(environment)
    for variable in merge_environment.keys():
        value = environment.setdefault(variable, '')

        if value:
            value += sep

        value += merge_environment[variable]

        merged_environment[variable] = value

    return merged_environment


def _overwrite_environment(environment, overwrite_environment):
    # type: (Dict[str, str], Dict[str, str]) -> Dict[str, str]
    if not overwrite_environment:
        return environment

    overwritten_environment = dict(environment)
    for variable in overwrite_environment.keys():
        overwritten_environment[variable] = overwrite_environment[variable]

    return overwritten_environment
