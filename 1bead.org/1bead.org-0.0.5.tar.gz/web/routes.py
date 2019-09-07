from aiohttp import web

from web.views import index


def setup_routes(app):
    # app.router.add_static('/static', path=PROJECT_ROOT / 'static', name='static')
    app.add_routes([web.get('/', index)])
