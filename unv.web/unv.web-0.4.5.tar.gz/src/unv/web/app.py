import os
import inspect
import asyncio

import uvloop
import jinja2
import aioredis

from pathlib import Path

from aiohttp import web

from unv.app.base import Application
from unv.app.settings import SETTINGS as APP_SETTINGS

from unv.deploy.settings import SETTINGS as APP_DEPLOY_SETTINGS

from .helpers import (
    url_for_static, url_with_domain, inline_static_from, make_url_for_func
)
from .deploy import SETTINGS as DEPLOY_SETTINGS
from .settings import SETTINGS


def setup_event_loop():
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    if APP_SETTINGS.is_dev:
        loop.set_debug(True)


def setup_jinja2(app: web.Application):
    if not SETTINGS.jinja2_enabled:
        return

    app['jinja2'] = jinja2.Environment(**SETTINGS.jinja2_settings)
    app['jinja2'].globals.update({
        'url_for': make_url_for_func(app),
        'url_for_with_domain': make_url_for_func(app, with_domain=True),
        'url_for_static': url_for_static,
        'url_with_domain': url_with_domain,
        'inline_static_from': inline_static_from,
        'is_dev': APP_SETTINGS.is_dev,
        'is_prod': APP_SETTINGS.is_prod,
        'is_test': APP_SETTINGS.is_test
    })


async def create_connection_pool(app):
    pool = await aioredis.create_redis_pool(
        (SETTINGS.redis_host, SETTINGS.redis_port),
        db=SETTINGS.redis_database,
        minsize=SETTINGS.redis_min_connections,
        maxsize=SETTINGS.redis_max_connections,
        loop=app.loop
    )
    app['redis'] = pool


async def close_connection_pool(app):
    pool = app['redis']
    pool.close()
    await pool.wait_closed()


def setup_redis(app: web.Application):
    if not SETTINGS.redis_enabled:
        return

    app.on_startup.append(create_connection_pool)
    app.on_cleanup.append(close_connection_pool)


def setup_static_dirs(app: Application):
    if not DEPLOY_SETTINGS.static_link:
        return

    for component in app.components:
        component_path = Path(inspect.getfile(component)).parent
        static_path = component_path / 'static'
        public_dir = DEPLOY_SETTINGS.static_dir
        public_app_dir = static_path / public_dir.name

        for directory in public_app_dir.glob('*'):
            os.system('mkdir -p {}'.format(public_dir))
            os.system('ln -sf {} {}'.format(directory, public_dir))


def run_web_app_task(app: web.Application):
    web.run_app(
        app,
        host=DEPLOY_SETTINGS.host,
        port=DEPLOY_SETTINGS.port + DEPLOY_SETTINGS.instance,
        access_log=None
    )


def setup(app: Application):
    app.register(web.Application())

    app.register_setup_task(setup_event_loop)
    app.register_setup_task(setup_jinja2)
    app.register_setup_task(setup_static_dirs)
    app.register_setup_task(setup_redis)

    app.register_run_task(run_web_app_task)
