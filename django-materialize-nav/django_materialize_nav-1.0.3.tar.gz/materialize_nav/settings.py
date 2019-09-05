from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static

__all__ = ['mysettings']


class Defaults(object):
    pass


class AppSettings(object):
    def __init__(self, defaults=None):
        self.defaults = defaults

    def __getattr__(self, name):
        default = getattr(self.defaults, name, None)
        return getattr(settings, name, default)

    def __dir__(self):
        return dir(self.defaults)


DEFAULTS = Defaults()
mysettings = AppSettings(DEFAULTS)


# ========== Defaults ==========
DEFAULTS.MATERIAL_ICONS_URL = {
    'href': 'https://fonts.googleapis.com/icon?family=Material+Icons'
    }

DEFAULTS.MATERIALIZE_CSS_URL = {
    'href': 'https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css',
    }

DEFAULTS.MATERIALIZE_JS_URL = {
    'src': 'https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js',
    }

DEFAULTS.MATERIALIZE_JQUERY_URL = {
    'src': 'http://code.jquery.com/jquery-3.3.1.min.js',
    'integrity': 'sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8=',
    'crossorigin': 'anonymous'
    }

DEFAULTS.MATERIALIZE_NAV_CSS_URL = {
    'href': static('materialize_nav/materialize_nav.css'),
    }

DEFAULTS.MATERIALIZE_NAV_JS_URL = {
    'src': static('materialize_nav/materialize_nav.js'),
    }

DEFAULTS.MATERIALIZE_NAV_COLOR_JS_URL = {
    'src': static('materialize_nav/materialize_nav_colors.js'),
    }

# ========== Styling ==========
DEFAULTS.MATERIALIZE_SITE_NAME = None
DEFAULTS.MATERIALIZE_TITLE = None
DEFAULTS.MATERIALIZE_HIDE_CONTAINER = False
DEFAULTS.MATERIALIZE_SHOW_SIDENAV = True
DEFAULTS.MATERIALIZE_FIXED_SIDENAV = False
DEFAULTS.MATERIALIZE_PRIMARY_COLOR = 'materialize-red lighten-2'
DEFAULTS.MATERIALIZE_SECONDARY_COLOR = 'teal'
DEFAULTS.MATERIALIZE_PRIMARY_COLOR_LIGHT = '#e51c23'
DEFAULTS.MATERIALIZE_PRIMARY_COLOR_DARK = None
DEFAULTS.MATERIALIZE_SUCCESS_COLOR = None
DEFAULTS.MATERIALIZE_ERROR_COLOR = None
DEFAULTS.MATERIALIZE_LINK_COLOR = None
