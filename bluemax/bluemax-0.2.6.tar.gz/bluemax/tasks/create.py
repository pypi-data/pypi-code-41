'''
    Tools to create a project
'''
import os
import logging
from pathlib import Path
from invoke import task
from .utils import Colored

LOGGER = logging.getLogger(__name__)


def get_venv():
    ''' return the current virtual environment local path '''
    result = '.'
    cwd = os.getcwd()
    venv = os.getenv('VIRTUAL_ENV')
    LOGGER.debug('cwd: %s', cwd)
    LOGGER.debug('venv: %s', venv)
    if venv != cwd and venv.startswith(cwd):
        # remove cwd and trailing sep
        result = venv[len(cwd) + 1 :]
    return result


@task(default=True)
def project(_, name, force=False, with_config=False):
    ''' Creates a project with procedures, services, settings and urls. '''
    print(f'Creates project: {Colored.blue(name)}')
    if os.path.exists(name) and force is False:
        print('that module already exists: ', Colored.pink(name))
    else:
        if not os.path.isdir(name):
            os.makedirs(name)
        with open(os.path.join(name, '__init__.py'), 'w') as file:
            file.write(
                '''""" A bluemax project """
VERSION = "0.0.1"
'''
            )
        with open(os.path.join(name, 'settings.py'), 'w') as file:
            if with_config is True:
                file.write(
                    '''""" add your settings here """
import os
import logging
import yaml
from bluemax.settings import merge_dict


def extend(settings):
    """ change settings """
    logging.info("extending settings")
    stage = os.getenv("STAGE", "dev")
    stage_file = f"conf/{stage}.yml"
    base_file = "conf/base.yml"
    if os.path.isfile(base_file):
        with open(base_file, "r") as file:
            loaded = yaml.safe_load(file)
            if loaded:
                merge_dict(settings, loaded)
            logging.info("loaded config: base")
    if os.path.isfile(stage_file):
        with open(stage_file, "r") as file:
            loaded = yaml.safe_load(file)
            if loaded:
                merge_dict(settings, loaded)
            logging.info("loaded config: %s ", stage)
    return settings
'''
                )
            else:
                file.write(
                    '''""" add your settings here """
import logging


def extend(settings):
    """ change settings """
    logging.info('extending settings')
    return settings
'''
                )
        with open(os.path.join(name, 'urls.py'), 'w') as file:
            file.write(
                '''""" add your tornado routes here """
import logging


def extend(urls):
    """ add tornado routes to urls """
    logging.info('extending urls')
    return urls
'''
            )
        with open(os.path.join(name, 'procedures.py'), 'w') as file:
            file.write(
                '''""" an example function and exposing it through __all__ """

__all__ = ['add']


def add(int_a: int, int_b: int) -> int:
    """ simple addition of two integers"""
    return int_a + int_b
'''
            )
        with open(os.path.join(name, 'services.py'), 'w') as file:
            file.write(
                '''""" an example service """
import asyncio
import time
from bluemax import context

__all__ = ["clock"]


async def clock():
    """ Will broadcast every 5 seconds """
    while True:
        context.broadcast('time', {'now': time.time()})
        await asyncio.sleep(5)
'''
            )
        with open(os.path.join(name, 'log.py'), 'w') as file:
            file.write(
                '''""" an example log setup """
import os
import yaml


def extend(config):  # pylint: disable=W0613
    """
    config is the existing logging configuration
    returning a dict will be used with dictConfig
    """
    if os.path.isfile("logging.yml"):
        with open("logging.yml", "r") as file:
            config = yaml.safe_load(file)
    return config
'''
            )
        if not os.path.isfile('Makefile'):
            virtual_env = get_venv()
            with open(os.path.join('Makefile'), 'w') as file:
                file.write(
                    f'''
SHELL := /bin/bash

lint:
\tsource {virtual_env}/bin/activate && flake8 .
\tsource {virtual_env}/bin/activate && pylint {name} tests

test:
\tsource {virtual_env}/bin/activate && \\
\tpy.test --cov {name} --cov-report term-missing tests

check: lint test

run:
\tsource {virtual_env}/bin/activate && \\
\t\tbluemax run.server -m {name}

build:
\tsource {virtual_env}/bin/activate && \\
\t\tpython setup.py sdist

full: check build

setup:
\tif which python3.7 && [ ! -d {virtual_env} ] ; then python3.7 -m venv {virtual_env} ; fi
\tsource {virtual_env}/bin/activate \\
\t\t&& python -m pip install -q -U pip \\
\t\t&& pip install -e .[dev]
'''
                )
    if with_config is True:
        config(_, name, force=force)


@task
def tests(_, name, force=False):
    ''' create a config folder with dev, staging & prod yamls '''
    print(f'gen test: {name}')
    test_dir = 'tests'
    if os.path.exists(test_dir) and force is False:
        print('that folder already exists:', test_dir)
    else:
        if not os.path.isdir(test_dir):
            os.makedirs(test_dir)
        Path(os.path.join(test_dir, '__init__.py')).touch()
        with open(os.path.join(test_dir, 'conftest.py'), 'w') as file:
            file.write(
                f'''
import pytest
from bluemax.web.server import make_app
from bluemax.settings import SETTINGS

@pytest.fixture
def app(io_loop):
    SETTINGS.update(
        {{
            "procedures": "{name}.procedures",
            "tornado": {{
                "auth_handler": None,
                "manager": "bluemax:ContextRpc",
                "static_dir": None,
            }},
            "redis_url": None,
        }}
    )
    result = make_app()
    return result
'''
            )
        with open(os.path.join(test_dir, f'test_web.py'), 'w') as file:
            file.write(
                '''
import logging
from urllib.parse import urlencode
from bluemax.web.server import BROADCASTER
from bluemax.web import json_utils
from bluemax import context

async def test_add(http_server_client):
    message = {"jsonrpc": "2.0", "id": "1a", "method": "add", "params": [2, 2]}
    response = await http_server_client.fetch(
        "/rpc", method="POST", body=json_utils.dumps(message)
    )
    assert json_utils.loads(response.body)["result"] == 4

    await context._MANAGER_.shutdown()
    await BROADCASTER.stop()
'''
            )


@task
def config(_, name, conf='conf', force=False):
    ''' create a config folder with dev, staging & prod yamls '''
    print(f'gen config: {conf}')
    if os.path.exists(conf) and force is False:
        print('that folder already exists: ', conf)
    else:
        if not os.path.isdir(conf):
            os.makedirs(conf)
        with open(os.path.join(conf, 'base.yml'), 'w') as file:
            file.write(
                '''---
DEBUG: false
'''
            )
        with open(os.path.join(conf, 'dev.yml'), 'w') as file:
            file.write(
                f'''---
debug: true
procedures: {name}.procedures
services: {name}.services
log_extend: null
settings_extend: null
urls_extend: null
tornado:
    auth_handler: null
    manager: bluemax.services:servicesrpc
    static_dir: null
    cookie_name: null
    cookie_secret: null
    login_url: null
    cognito_oauth:
        key: null
        secret: null
        redirect_url: null
        endpoint: null
port: 8080
max_workers: 4
max_threads: 4
redis_url: none
redis_broadcast_q: broadcast
redis_work_q: perform
redis_services_q: services
'''
            )
        with open(os.path.join(conf, 'staging.yml'), 'w') as file:
            file.write(
                '''---
'''
            )
        with open(os.path.join(conf, 'prod.yml'), 'w') as file:
            file.write(
                '''---
'''
            )


@task
def docker(_, name, force=False):
    ''' create a config folder with dev, staging & prod yamls '''
    docker_file = 'Dockerfile'
    print(f'gen docker: {docker_file}')
    if os.path.isfile(docker_file) and force is False:
        print('that file already exists: ', docker_file)
    else:
        with open(docker_file, 'w') as file:
            file.write(
                '''# Use an official Python runtime as a parent image
FROM python:3.7-slim
RUN apt-get update && apt-get install -y git

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# upgrade pip to make sure it can use git repos
RUN pip install --upgrade pip
RUN pip install bluemax

# Install any needed packages
RUN [ -f requirements.txt ] && pip install -r requirements.txt ||  echo "No requirements.txt"

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV PYTHONPATH ".:${PYTHONPATH}"
ENV PORT 80

'''
            )
        print(f'gen docker: docker-compose.yml')
        with open('docker-compose.yml', 'w') as file:
            file.write(
                f'''version: '3'
services:
  web:
    build: .
    image: {name}:latest
    container_name: {name}-web
    command: bluemax run -m {name}
    ports:
      - "8080:80"
'''
            )

