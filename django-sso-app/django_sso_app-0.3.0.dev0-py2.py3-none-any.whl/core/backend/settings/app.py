import environ

env = environ.Env()

from .settings import * # django defaults
from .logging import *

from django_sso_app.app.settings import *

DJANGO_SSO_APP_ENABLED = env.bool('DJANGO_SSO_APP_ENABLED', default=True)

gettext = lambda s: s

TESTING_MODE = 'test' in sys.argv or DEBUG

SITE_ID = 1

LANGUAGES = (
    ## Customize this
    ('it', gettext('it')),
    ('en-gb', gettext('en')),
    ('es', gettext('es')),
    ('pt', gettext('pt')),
    ('fr', gettext('fr')),
    ('de', gettext('de')),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'core', 'locale'),
)

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

APP_DOMAIN = os.environ.get('APP_DOMAIN', 'localhost:8000')

# email
DEFAULT_FROM_EMAIL = os.environ.get('DJANGO_DEFAULT_FROM_EMAIL', 'noreply@example.com')

# sendgrid
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY=os.environ.get("SENDGRID_API_KEY", "")
#SENDGRID_SANDBOX_MODE_IN_DEBUG=False # defaults to True

if DEBUG or os.environ.get('DJANGO_CONSOLE_EMAIL_BACKEND', None):
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


EMAILS_DOMAIN = os.environ.get('EMAILS_DOMAIN', APP_DOMAIN) # domain name specified in email templates
EMAILS_SITE_NAME = os.environ.get('EMAILS_SITE_NAME', EMAILS_DOMAIN) # site name specified in email templates

COOKIE_DOMAIN = "example.com"

INSTALLED_APPS += [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    'django_sso_app.core.apps.groups',
    'django_sso_app.core.apps.frontend',
    'django_sso_app.app.profiles',
]


# djangorestframework

DRF_DEFAULT_AUTHENTICATION_CLASSES = [
    'rest_framework.authentication.TokenAuthentication'
]
DRF_DEFAULT_AUTHENTICATION_CLASSES = ['django_sso_app.app.profiles.authentication.DjangoSsoAppAuthentication'] + DRF_DEFAULT_AUTHENTICATION_CLASSES

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': DRF_DEFAULT_AUTHENTICATION_CLASSES,
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),

    'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S%z',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    # https://www.django-rest-framework.org/community/3.10-announcement/#continuing-to-use-coreapi
}

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    'django_sso_app.app.profiles.backends.DjangoSsoAppBackend',
]

TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'django_sso_app.app.profiles.context_processors.sso_cookie_domain',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.locale.LocaleMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

]

if DJANGO_SSO_APP_ENABLED:
    MIDDLEWARE += [
        'django_sso_app.app.profiles.middleware.DjangoSsoAppMiddleware',
    ]

MIDDLEWARE += [
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# AUTH_USER_MODEL = 'auth.User'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, "core", "backend", 'app.db.sqlite3'),
    }
}
