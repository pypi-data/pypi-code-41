import environ

env = environ.Env()

from .settings import * # django defaults
from .logging import *

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
    os.path.join(BASE_DIR, 'locale'),
)

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

APP_DOMAIN = os.environ.get('APP_DOMAIN', 'localhost:8000')

# django-sso
DJANGO_SSO_BACKEND_ENABLED = True
DJANGO_SSO_APP_ENABLED = env.bool('DJANGO_SSO_APP_ENABLED', default=not DJANGO_SSO_BACKEND_ENABLED)

if DJANGO_SSO_BACKEND_ENABLED:
    from pai_sso.core.settings import *
if DJANGO_SSO_APP_ENABLED:
    from pai_sso.app.settings import *


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
]

if DJANGO_SSO_BACKEND_ENABLED:

    INSTALLED_APPS += [
        'rest_framework',
        'rest_framework.authtoken',
        'rest_auth',

        'allauth.socialaccount',

        'rest_auth.registration',
        'rest_framework_swagger',

        'corsheaders',

        'pai_sso.core.apps.services',
        'pai_sso.core.apps.devices',
        'pai_sso.core.apps.passepartout',

        'pai_sso.core.apps.users',
        'pai_sso.core.apps.groups',

        DJANGO_SSO_FRONTEND_APP,
    ]

    if DJANGO_SSO_APIGW_ENABLED:
        INSTALLED_APPS += [
            'pai_sso.core.apps.api_gateway.kong',
        ]

    AUTH_USER_MODEL = 'users.User'

if DJANGO_SSO_APP_ENABLED:
    INSTALLED_APPS += [
        'pai_sso.core.apps.groups',
        'pai_sso.app.profiles',
    ]


# djangorestframework

DRF_DEFAULT_AUTHENTICATION_CLASSES = [
    'rest_framework.authentication.TokenAuthentication'
]

if DEBUG:
    DRF_DEFAULT_AUTHENTICATION_CLASSES = ['rest_framework.authentication.SessionAuthentication'] + DRF_DEFAULT_AUTHENTICATION_CLASSES

if DJANGO_SSO_BACKEND_ENABLED:
    DRF_DEFAULT_AUTHENTICATION_CLASSES = DRF_DEFAULT_AUTHENTICATION_CLASSES + [
        'pai_sso.core.apps.users.authentication.UsersAuthentication',
    ]
elif DJANGO_SSO_APP_ENABLED:
    DRF_DEFAULT_AUTHENTICATION_CLASSES = ['django_sso_app.authentication.DjangoSsoAppAuthentication'] + DRF_DEFAULT_AUTHENTICATION_CLASSES


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


# allauth
AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
]

if DJANGO_SSO_BACKEND_ENABLED:
    AUTHENTICATION_BACKENDS += [
        # `allauth` specific authentication methods, such as login by e-mail
        'allauth.account.auth_backends.AuthenticationBackend',
    ]

if DJANGO_SSO_APP_ENABLED:
    AUTHENTICATION_BACKENDS + AUTHENTICATION_BACKENDS + [
        'pai_sso.app.profiles.backends.DjangoSsoAppBackend',
    ]
    TEMPLATES[0]['OPTIONS']['context_processors'] += [
        'pai_sso.app.profiles.context_processors.sso_cookie_domain',
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
        'pai_sso.app.profiles.middleware.DjangoSsoAppMiddleware',
    ]

MIDDLEWARE += [
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'

ACCOUNT_AUTHENTICATION_METHOD='username_email'
ACCOUNT_EMAIL_REQUIRED=True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_ADAPTER='pai_sso.core.backend.adapter.UserAdapter'
ACCOUNT_CONFIRM_EMAIL_ON_GET=True
ACCOUNT_EMAIL_VERIFICATION='mandatory'
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS=False
#ACCOUNT_SESSION_REMEMBER=False
#AUTHENTICATED_LOGIN_REDIRECTS=True
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = LOGIN_URL
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = LOGIN_URL
ACCOUNT_SESSION_REMEMBER=False

ACCOUNT_FORMS = {
    'signup': 'pai_sso.core.backend.forms.SignupForm'
}


# rest_auth

REST_USE_JWT = True
REST_AUTH_SERIALIZERS = {
    'LOGIN_SERIALIZER': 'pai_sso.core.backend.serializers.LoginSerializer',
    'USER_DETAILS_SERIALIZER' : 'pai_sso.core.apps.users.serializers.UserSerializer',
    'PASSWORD_RESET_SERIALIZER': 'pai_sso.core.backend.serializers.PasswordResetSerializer'
}

REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'pai_sso.core.backend.serializers.RegisterSerializer',
}

JWT_AUTH = {
    'JWT_AUTH_COOKIE': 'jwt',

    'JWT_PAYLOAD_HANDLER': 'pai_sso.core.backend.handlers.jwt_payload_handler',
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_VERIFY': False,
}



