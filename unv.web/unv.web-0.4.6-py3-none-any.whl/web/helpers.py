import urllib

from aiohttp import web

from unv.utils.files import calc_crc32_for_file

from .deploy import SETTINGS as DEPLOY_SETTINGS


async def render_template(
        request, template_name, context=None, status=web.HTTPOk.status_code):
    template = request.app['jinja2'].get_template(template_name)
    return web.Response(
        text=await template.render_async(context or {}),
        status=status, charset='utf-8',
        content_type='text/html'
    )


def url_for_static(path: str, with_hash: bool = False):
    url = DEPLOY_SETTINGS.static_url
    directory = DEPLOY_SETTINGS.static_dir
    real_path = directory / path.lstrip('/')
    hash_ = ''

    if with_hash:
        hash_ = '?hash={}'.format(calc_crc32_for_file(real_path))
    path = str(path).replace(str(directory), '', 1).lstrip('/')

    return f"{url}/{path}{hash_}"


def url_with_domain(path: str):
    protocol = 'http'
    path = path.lstrip('/')
    if DEPLOY_SETTINGS.use_https:
        protocol = 'https'
    return f'{protocol}://{DEPLOY_SETTINGS.domain}/{path}'


def make_url_for_func(app, with_domain=False):
    def url_for(route, **parts):
        parts = {key: str(value) for key, value in parts.items()}
        url = app.router[route].url_for(**parts)
        if with_domain:
            url = url_with_domain(str(url))
        return url
    return url_for


def inline_static_from(path):
    with (DEPLOY_SETTINGS.static_dir / path).open('r') as f:
        return f.read().replace("\n", "")
