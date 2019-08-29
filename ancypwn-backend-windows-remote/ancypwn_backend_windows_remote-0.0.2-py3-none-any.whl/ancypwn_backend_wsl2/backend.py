import docker
import appdirs
import os
import importlib
import pathlib
import sys
import pywintypes

import win32api
import win32process

from ancypwn.server import ServerProcess
from ancypwn.util import _read_container_name, _make_sure_directory


APPNAME = 'ancypwn'
APPAUTHOR = 'Anciety'


TEMP_DIR = appdirs.user_cache_dir(APPNAME, APPAUTHOR)

EXIST_FLAG = os.path.join(TEMP_DIR, 'ancypwn.id')
DAEMON_PID = os.path.join(TEMP_DIR, 'ancypwn.daemon.pid')


class AlreadyRuningException(Exception):
    pass


class NotRunningException(Exception):
    pass


def _start_service(port):
    """starts service of waiting for opening new terminals
    """
    cmd = 'python {} {}'.format(os.path.realpath(__file__), port) 
    info = win32process.CreateProcess(
        None,
        cmd,
        None,
        None,
        0,
        win32process.CREATE_NO_WINDOW,
        None,
        None,
        win32process.STARTUPINFO())


def _end_service():
    """ends the terminal service
    """
    with open(DAEMON_PID, 'r') as f:
        pid = f.read()

    try:
        h = win32api.OpenProcess(1, False, int(pid))
    except pywintypes.error as e:
        if e.winerror == 87:
            # already not existing
            return

    win32api.TerminateProcess(h, 0)
    win32api.CloseHandle(h)


def _win_dir_to_wsl(directory):
    """windows directory to wsl
    Example:
        D:\\x -> /mnt/d/x
    """
    directory = os.path.realpath(os.path.expanduser(directory))
    directory = directory.replace(":\\", '\\')
    directory = directory.replace('\\', '/')
    return '/mnt/{}'.format(directory[0].lower()) + directory[1:]


def _figure_volumes(directory):
    """figures out the volumes to be binded

    """
    directory = _win_dir_to_wsl(directory)
    volumes = {
        directory: {
            'bind': '/pwn',
            'mode': 'rw'
        }
    }
    return volumes


def _attach_interactive(url, name, command):
    if command != '':
        cmd = 'powershell.exe -NoExit -Command docker -H {} exec -it {} bash -c \'{}\''.format(url, name, repr(command)[1:-1])
    else:
        cmd = 'powershell.exe -NoExit -Command docker -H {} exec -it {} bash'.format(url, name, command)
    os.system(cmd)


def _run_container(url, image_name, volumes, privileged, command):
    """does run the container
    """
    client = docker.DockerClient(base_url=url)
    container = client.containers
    running = container.run(
            image_name,
            '/bin/bash',
            cap_add=['SYS_ADMIN', 'SYS_PTRACE'],
            detach=True,
            tty=True,
            volumes=volumes,
            privileged=privileged,
            network_mode='host',
            remove=True,
            )

    with open(EXIST_FLAG, 'w') as flag:
        flag.write(running.name)

    _attach_interactive(url, running.name, command)


def run(config=None, directory=None, image_name=None, priv=None, command=None):
    directory = os.path.abspath(directory) 
    if not os.path.exists(directory):
        raise IOError('direcotry to bind not exist')
    

    _make_sure_directory(EXIST_FLAG)
    if os.path.exists(EXIST_FLAG):
        raise AlreadyRuningException('ancypwn is already running, you should either end it or attach to it')

    _start_service(config['terminal_port'])
    volumes = _figure_volumes(directory)
    try:
        _run_container(config['backend']['url'], image_name, volumes, priv, command)
    except Exception as e:
        _end_service()
        raise e


def attach(config, command):
    container_name = _read_container_name(EXIST_FLAG)
    client = docker.DockerClient(base_url=config['backend']['url'])
    container = client.containers
    conts = container.list(filters={'name': container_name})
    if len(conts) != 1:
        raise Exception('multiple images of name {} found, unable to execute'.format(image_name))

    _attach_interactive(config['backend']['url'], conts[0].name, command)


def end(config):
    client = docker.DockerClient(base_url=config['backend']['url'])
    container = client.containers
    container_name = _read_container_name(EXIST_FLAG)
    conts = container.list(filters={'name': container_name})
    if len(conts) < 1:
        os.remove(EXIST_FLAG)
        raise NotRunningException('not running')

    conts[0].stop()
    os.remove(EXIST_FLAG)
    _end_service()


def _run_server(port):
    server = ServerProcess(port)
    server.start()
    _make_sure_directory(DAEMON_PID)
    with open(DAEMON_PID, 'w') as f:
        f.write(str(server.pid))
    server.join()


if __name__ == '__main__':
    # argv[1] -> port
    _run_server(int(sys.argv[1]))
