""" root level task - not imported with module """
import os
import signal
import logging
from invoke import task

LOGGER = logging.getLogger(__name__)


@task(help={
    "process": "server, worker or services"
})
def stop(ctx, process):
    """ stop a running server, worker or services """
    pid_file = f"{process}.pid"
    try:
        with open(pid_file, 'r') as f:
            contents = f.read()
        pid = int(contents)
        os.kill(pid, signal.SIGINT)
        os.remove(pid_file)
    except Exception:  # pylint: disable=W0703
        LOGGER.exception('problem with %s', pid_file)
