from django import template
from django.utils.html import format_html
from psu_base.services import utility_service
from psu_base.classes.Log import Log

log = Log()


def wdt_url(version=None):
    return utility_service.get_static_content_url() + "/wdt/v{}".format(str(version) if version else '1')


def jquery(*args, **kwargs):
    url = utility_service.get_static_content_url() + '/wdt/jquery/'

    if 'version' in kwargs and kwargs['version'] is not None:
        file_name = "jquery-{}.min.js".format(kwargs['version'].strip())
    else:
        file_name = 'jquery.min.js'

    return format_html(f"""<script src="{url}{file_name}"></script>""")


def bootstrap(*args, **kwargs):
    url = utility_service.get_static_content_url() + '/wdt/bootstrap/'
    if 'version' in kwargs and kwargs['version'] is not None:
        url += "{}/".format(kwargs['version'])

    return format_html(
        f"""
        <script src="{url}js/bootstrap.js"></script>
        <link rel="stylesheet" href="{url}css/bootstrap.css" />
        """
    )


def font_awesome(*args, **kwargs):
    url = utility_service.get_static_content_url() + '/wdt/fontawesome/'
    if 'version' in kwargs and kwargs['version'] is not None:

        # FontAwesome 4 is CSS rather than SVG
        if kwargs['version'] == '4':
            return format_html(
                f"""<link rel="stylesheet" href="{url}4/css/font-awesome.min.css" />"""
            )

        else:
            url += "{}/js/all.js".format(kwargs['version'])
    else:
        url += "recent/js/all.js"

    return format_html(
        f"""<script defer src="{url}"></script>"""
    )


def wdt_stylesheet(css_file, version=None):
    url = wdt_url(version)
    return format_html(
        f"<link rel=\"stylesheet\" href=\"{url}/styles/{css_file}\" />"
    )


def wdt_javascript(js_file, version=None):
    url = wdt_url(version)
    return format_html(
        f"""
        <script src="{url}/javascript/{js_file}"></script>
        """
    )
