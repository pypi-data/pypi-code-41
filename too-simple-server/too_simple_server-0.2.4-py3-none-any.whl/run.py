"""Server control"""
import os
import signal

from lockfile.pidlockfile import PIDLockFile
from wsgiserver import WSGIServer

from .api import SERVER
from .configuration import DEFAULT_CFG_PATH, load_configuration
from .database import init_db


def _try_dir(default, fallback):
    file_name = f"{default}/randomfilename"
    try:
        os.makedirs(default, exist_ok=True)
        open(file_name, "w+").close()
        os.remove(file_name)
        return default
    except (IOError, PermissionError):
        os.makedirs(fallback, exist_ok=True)
        return fallback


def _pid_dir():
    return _try_dir("/tmp/too-simple", os.path.expanduser("~/.too-simple"))


def _log_dir():
    return _try_dir("/var/log/too-simple", os.path.expanduser("~/.too-simple"))


PID_FILE = os.path.abspath(f"{_pid_dir()}/web-server.pid")
LOG_FILE = os.path.abspath(f"{_log_dir()}/execution.log")


def main(action, debug=None, configuration_path=DEFAULT_CFG_PATH, no_wsgi=False):
    """Start/stop running server"""
    import daemon  # *nix only

    configuration = load_configuration(configuration_path)
    if debug is not None:
        configuration.debug = debug

    def _stop():
        with open(PID_FILE) as pid_file:
            pid = int(pid_file.read())
        os.kill(pid, signal.SIGTERM)

    def _start():
        init_db(configuration)
        with open(LOG_FILE, "w+") as log_file, \
                daemon.DaemonContext(pidfile=PIDLockFile(PID_FILE),
                                     detach_process=True,
                                     stdout=log_file, stderr=log_file):
            if no_wsgi:
                SERVER.run("0.0.0.0", configuration.server_port)
            else:
                WSGIServer(SERVER, port=configuration.server_port).start()

    if action == "start":
        _start()
    elif action == "stop":
        _stop()
    elif action == "restart":
        _stop()
        _start()
    else:
        raise AttributeError(f"Unknown action: {action}")
