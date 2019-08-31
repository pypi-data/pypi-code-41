import enum
import logging
import platform
import subprocess
import sys
from typing import Optional

from klisch import logger

log = logger.get(__file__, logging.DEBUG)


class Platform(enum.Enum):
    WINDOWS = 'Windows'
    LINUX = 'Linux'
    WSL = 'Windows Subsystem for Linux'
    LSF = 'Platform Load Sharing Facility'


class Shell(enum.Enum):
    TCSH = 'tcsh'
    BASH = 'bash'
    DASH = 'dash'
    FISH = 'fish'
    ZSH = 'zsh'
    CMD = 'cmd'


def subprocess_run(args, capture_output=True, text=False, **kwargs):
    # TODO: can upgrade arguments till runtime at Python 3.7
    #  subprocess.run(..., capture_output=True, text=True)
    stdout = subprocess.PIPE if capture_output else None
    stderr = subprocess.PIPE if capture_output else None
    process = subprocess.run(
        args, stdout=stdout, stderr=stderr, universal_newlines=text, **kwargs
    )
    return process


def get_usable_python3(python_command: str) -> Optional[str]:
    try:
        proc = subprocess_run([python_command, '-V'], text=True)
        output = str(proc.stderr) or str(proc.stdout)
        log.debug(f'stdout: {proc.stdout.strip()}, stderr: {proc.stderr.strip()}')
    except FileNotFoundError as e:
        output = ''
        log.exception(e)
    return python_command if 'Python 3' in output else None


def get_usable_lsf(lsf_command):
    try:
        proc = subprocess_run([lsf_command, '-V'], text=True)
        if str(proc.stderr):
            return lsf_command
    except FileNotFoundError:
        return None


def get_shell_output(shell_executoble=None, command=None) -> Optional[str]:
    try:
        command = command or 'echo $0'
        proc = subprocess_run(
            command, text=True, shell=True, executable=shell_executoble
        )
        stdout = proc.stdout.strip()
        return stdout if stdout != '$0' else None
    except FileNotFoundError:
        return None


def get_platform() -> Platform:
    system = platform.system()
    if 'Microsoft' in platform.release():
        return Platform.WSL
    elif get_usable_lsf('bsub'):
        return Platform.LSF
    else:
        return Platform(system)


def get_available_shell():
    avail_shells = set()

    if get_platform() == Platform.WINDOWS:
        avail_shells.add(Shell.CMD)
    if get_shell_output():
        avail_shells.add(Shell.DASH)
    for executable, test_command, shell in [
        ('/bin/bash', 'echo $BASH', Shell.BASH),
        ('/bin/tcsh', 'echo $shell', Shell.TCSH),
        ('/usr/bin/zsh', 'echo $ZSH_NAME', Shell.ZSH),
        ('/usr/bin/fish', 'echo $FISH_VERSION', Shell.FISH),
    ]:
        specific_shell_check = get_shell_output(executable, command=test_command)
        optional_shell_check = get_shell_output(executable)
        if executable == '/usr/bin/fish':
            optional_shell_check = True
        if specific_shell_check and optional_shell_check:
            avail_shells.add(shell)

    return avail_shells


PLATFORM = get_platform()
AVAIL_SHELLS = get_available_shell()
PYTHON = get_usable_python3('python3') or get_usable_python3('python') or sys.executable
BSUB = get_usable_lsf('bsub')


if __name__ == '__main__':
    print('Platform', PLATFORM)
    print('Avail shells', AVAIL_SHELLS)
    print('Python3', PYTHON)
    print('Bsub', BSUB)
