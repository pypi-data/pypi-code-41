"""
    Common functions used by Click and Invoke
"""
import os
import logging
import logging.config
import importlib
from contextlib import contextmanager
from bluemax.settings import extend

LOGGER = logging.getLogger(__name__)


class Colored:
    """ sometimes you need to colour console output """

    @staticmethod
    def green(text):
        """ turns text green """
        return f"\033[92m{text}\033[0m"

    @staticmethod
    def red(text):
        """ turns text red """
        return f"\033[91m{text}\033[0m"

    @staticmethod
    def blue(text):
        """ turns text blue """
        return f"\033[94m{text}\033[0m"

    @staticmethod
    def cyan(text):
        """ turns text cyan """
        return f"\033[36m{text}\033[0m"

    @staticmethod
    def gray(text):
        """ turns text gray """
        return f"\033[90m{text}\033[0m"

    @staticmethod
    def pink(text):
        """ turns text pink """
        return f"\033[33m{text}\033[0m"


@contextmanager
def pid_file(path):
    """ creates a file with the process id and removes it """
    pid = os.getpid()
    with open(path, "w") as file:
        file.write(f"{pid}")
    try:
        yield
    finally:
        if os.path.isfile(path):
            os.unlink(path)


def import_module(name):
    "Its ok not to have the module but not ok to not have dependants."
    try:
        logging.debug("looking for module %s", name)
        return importlib.import_module(name)
    except ModuleNotFoundError as ex:
        if name not in str(ex):
            raise


def get_module(name):
    """ import the project and return configuration options """
    options = {}
    if name is None:
        print("module expected")
    else:
        importlib.import_module(name)
        procs = importlib.import_module(f"{name}.procedures")
        if procs:
            if not getattr(procs, "__all__"):
                print(f"expected __all__ in procedures module")
            else:
                options["procedures"] = f"{name}.procedures"
                ext_log = import_module(f"{name}.log")
                if ext_log:
                    options["log_extend"] = f"{name}.log:extend"
                ext_settings = import_module(f"{name}.settings")
                if ext_settings:
                    options["settings_extend"] = f"{name}.settings:extend"
                ext_urls = import_module(f"{name}.urls")
                if ext_urls:
                    options["urls_extend"] = f"{name}.urls:extend"
        else:
            print(f"expected procedures in {name}")
    return options


def extend_logging(options):
    """ extend the logging and call dictConfig if response """
    if options.get("log_extend"):
        config = extend(options["log_extend"], {})
        if config:
            LOGGER.debug("logging.config %s", config)
            logging.config.dictConfig(config)


def confirm_action(action):
    """ Are you sure? """
    choice = ""
    while choice not in ["y", "n"]:
        choice = input(f"{action} [Y/N] ").lower()
    return choice == "y"
