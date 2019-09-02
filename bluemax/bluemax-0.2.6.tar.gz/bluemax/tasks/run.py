# pylint: disable=W0621
"""
    Task for the running of bluemax
    The load order:
        if module:
            load module
            load settings
            extend setting
            load logging
            run target
        else
            load settings
            load module
            extend settings
            load logging
            run target
"""
import logging
from importlib import import_module
import yaml
from invoke import task
from bluemax import settings
from bluemax.utils.describe import describe
from .utils import get_module, pid_file, extend_logging, Colored

LOGGER = logging.getLogger(__name__)


def bring_up(module=None, config=None):
    """ the standard bring up order """
    if settings.SETTINGS:
        # only bring-up once
        return
    if config:
        settings.init_settings(config)
    if module is None:
        module = settings.SETTINGS["procedures"]
    assert module, "module required"
    mod = get_module(module)
    if mod:
        settings.SETTINGS.update(mod)
    extend_settings = settings.get_settings("settings_extend")
    if extend_settings:
        settings.extend(extend_settings, settings.SETTINGS)
    extend_logging(settings.SETTINGS)


@task
def config(_, module=None, config=None, services=None):
    """ displays resultant config """
    bring_up(module, config)
    LOGGER.info("\n---\n%s", yaml.dump(settings.SETTINGS))
    mod = import_module(settings.get_settings("procedures"))
    print(Colored.blue("available:"))
    for description in describe(mod).values():
        print("  ", description)
    services = settings.get_settings("services", services)
    if services:
        services = import_module(services)
        print(Colored.blue("services:"))
        for description in describe(services).values():
            print("  ", description)
    print("", flush=True)


@task(
    default=True,
    help={
        "pid": "/path/to/pid/file",
        "module": "module to remote",
        "services": "services module",
        "config": "path to config.yml",
    },
)
def server(_, module=None, pid="server.pid", services=None, config=None):
    """ runs a bluemax server with optional services """
    bring_up(module, config)
    if services:
        settings.SETTINGS["services"] = services

    from bluemax.web import server as m_server
    with pid_file(pid):
        m_server.main()


@task(
    help={
        "pid": "/path/to/pid/file",
        "module": "module to remote",
        "services": "services module",
        "config": "path to config.yml",
    }
)
def worker(_, module=None, pid="worker.pid", config=None):
    """ runs a bluemax worker """
    bring_up(module, config)

    from bluemax.work import worker as m_worker
    with pid_file(pid):
        m_worker.main()


@task(
    help={
        "pid": "/path/to/pid/file",
        "module": "services module",
        "config": "path to config.yml",
    }
)
def services(_, module=None, pid="services.pid", services=None, config=None):
    """ runs a bluemax services """
    bring_up(module, config)

    from bluemax.services import server as s_worker
    if services:
        settings.SETTINGS["services"] = services
    with pid_file(pid):
        s_worker.main()

