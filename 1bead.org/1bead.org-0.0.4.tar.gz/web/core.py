from aiohttp import web
import aiohttp_jinja2
import jinja2

from web.routes import setup_routes
from web.constants import PROJECT_ROOT


app = web.Application()

aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(str(PROJECT_ROOT / 'web' / 'templates')))
setup_routes(app)
