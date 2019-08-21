"""
Useful functions needed by the module.
"""

import os
import socket

from datetime import date, datetime
from importlib import import_module


def which(program):
    """
    Fetch for the absolute path of a binary, same as `which` Unix command.

    :param program: Name of the program
    :type program: str
    :return: Absolute path of the program, or None if path not found.
    :rtype: str

    :Example:

    >>> which("ls")
    /bin/ls
    """

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, _ = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def hostname():
    """
    Return the hostname of the current machine.

    :return: the hostname of the current machine
    :rtype: str
    """
    if socket.gethostname().find(".") >= 0:
        return socket.gethostname()
    else:
        return socket.gethostbyaddr(socket.gethostname())[0]


def render(template):
    """
    Format the template using the hostname variable and date of the day.

    :param template: string to format
    :param template: string to format

    :return: the rendered template
    :rtype: str

    :Example:
    >>> render("machine-{hostname}-{date}")
    >>> render("machine-{hostname}-{datetime}") # using ISO format
    """
    return template.format(
        hostname=hostname(), date=date.today(), datetime=datetime.utcnow().isoformat()
    )


def load(name, pkg="", suffix="Task"):
    """
    Dynamically creates a list of all class from a module.

    :param name: Name of the driver.
    :param pkg: Absolute name of the module.
    :param suffix: String part in the name of each class to load.

    :type name: str
    :type pkg: str
    :type suffix: str

    :return: The task
    :rtype: class
    """
    class_name = "{}{}".format(name.capitalize(), suffix.capitalize())
    module = import_module("." + class_name, package=pkg)
    return getattr(module, class_name)
