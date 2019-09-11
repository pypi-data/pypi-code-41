"""
Base settings to build other settings files upon.
"""

import os
import sys
import environ

ROOT_DIR = (
    environ.Path(__file__) - 4
)  # (django_sso_app/config/settings/base.py - 3 = django_sso_app/)
APPS_DIR = ROOT_DIR.path("backend")

env = environ.Env()

gettext = lambda s: s

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(ROOT_DIR.path(".env")))

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", True)
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = env("DJANGO_TIME_ZONE", default="UTC") # pai
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = env("DJANGO_LANGUAGE_CODE", default="en-us") # pai
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = env.int("DJANGO_SITE_ID", default=1) # pai
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
# https://docs.djangoproject.com/en/dev/ref/settings/#locale-paths
LOCALE_PATHS = [APPS_DIR.path("locale")]

#pai
TESTING_MODE = 'test' in sys.argv or DEBUG

DJANGO_ALLAUTH_ENABLED = env.bool('DJANGO_ALLAUTH_ENABLED', default=True)
DJANGO_SSO_BACKEND_ENABLED = env.bool('DJANGO_SSO_BACKEND_ENABLED', default=True)
DJANGO_SSO_APP_ENABLED = env.bool('DJANGO_SSO_APP_ENABLED', default=True)

if DJANGO_SSO_BACKEND_ENABLED:
    from django_sso_app.backend.settings import *

if DJANGO_SSO_APP_ENABLED:
    from django_sso_app.app.settings import *


# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(ROOT_DIR, 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        "default": env.db("DATABASE_URL", default="postgres:///django_sso_app")
    }
    DATABASES["default"]["ATOMIC_REQUESTS"] = True

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "django_sso_app.backend.config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "django_sso_app.backend.config.wsgi.application"

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "django.contrib.humanize", # Handy template tags
    "django.contrib.admin",
]
THIRD_PARTY_APPS = [
    "crispy_forms",
    # pai
    "corsheaders",
]

if DJANGO_ALLAUTH_ENABLED:
    THIRD_PARTY_APPS += [
        "allauth",
        "allauth.account",
        "allauth.socialaccount",
    ]

THIRD_PARTY_APPS += [
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_swagger",

    "django_filters",
    "django_celery_beat",
]

LOCAL_APPS = [
    # Your stuff: custom apps go here
]

# django-sso-app
if DJANGO_SSO_BACKEND_ENABLED or DJANGO_SSO_APP_ENABLED:
    LOCAL_APPS += [
        "rest_auth",
        "rest_auth.registration",

        "django_sso_app.core.apps.groups",

        DJANGO_SSO_FRONTEND_APP
    ]
if DJANGO_SSO_BACKEND_ENABLED:
    LOCAL_APPS += DJANGO_SSO_BACKEND_CORE_APPS
if DJANGO_SSO_APP_ENABLED:
    LOCAL_APPS += DJANGO_SSO_APP_CORE_APPS

# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIGRATIONS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules
# MIGRATION_MODULES = {"sites": "backend.contrib.sites.migrations"} # pai

# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = "users.User"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = "/profile/"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = "/login/"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
"""
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]"""
# django
"""
[
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.UnsaltedSHA1PasswordHasher',
    'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
]
"""
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',

    'django.contrib.auth.hashers.SHA1PasswordHasher'
]

# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    # pai
    "django_sso_app.backend.middleware.x_forwarded_for.middleware.XForwardedForMiddleware",

    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # pai
    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]
# pai
if DJANGO_SSO_APP_ENABLED and not DJANGO_SSO_BACKEND_ENABLED:
    MIDDLEWARE.append('django_sso_app.app.middleware.DjangoSsoAppMiddleware')

MIDDLEWARE += [
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR("static"))
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(APPS_DIR.path("static"))]
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(ROOT_DIR("media"))
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        "DIRS": [str(APPS_DIR.path("templates"))],
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",

                # pai
                'django_sso_app.core.context_processors.get_repository_rev',
                'django_sso_app.core.context_processors.get_auth_settings',
            ],
        },
    }
]
# http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = "bootstrap4"

# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = (str(APPS_DIR.path("fixtures")),)

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-browser-xss-filter
SECURE_BROWSER_XSS_FILTER = True
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = "DENY"

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
# https://docs.djangoproject.com/en/2.2/ref/settings/#email-timeout
EMAIL_TIMEOUT = 5

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = "admin/"
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [("""Luca Bertuol""", "paiuolo@gmail.com")]
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "%(process)d %(thread)d %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
}

# Celery
# ------------------------------------------------------------------------------
if USE_TZ:
    # http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-timezone
    CELERY_TIMEZONE = TIME_ZONE
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-broker_url
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/0")
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_backend
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-accept_content
CELERY_ACCEPT_CONTENT = ["json"]
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-task_serializer
CELERY_TASK_SERIALIZER = "json"
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_serializer
CELERY_RESULT_SERIALIZER = "json"
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-time-limit
# TODO: set to whatever value is adequate in your circumstances
CELERY_TASK_TIME_LIMIT = env("CELERY_TASK_TIME_LIMIT", default=(5 * 60))
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-soft-time-limit
# TODO: set to whatever value is adequate in your circumstances
CELERY_TASK_SOFT_TIME_LIMIT = env("CELERY_TASK_SOFT_TIME_LIMIT", default=60)
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#beat-scheduler
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"


EMAILS_DOMAIN = os.environ.get('EMAILS_DOMAIN', APP_DOMAIN) # domain name specified in email templates
EMAILS_SITE_NAME = os.environ.get('EMAILS_SITE_NAME', EMAILS_DOMAIN) # site name specified in email templates

# lang

LANGUAGES = (
    ## Customize this
    ('it', gettext('it')),
    ('en-gb', gettext('en')),
    ('es', gettext('es')),
    ('pt', gettext('pt')),
    ('fr', gettext('fr')),
    ('de', gettext('de')),
)

# pai
if DJANGO_ALLAUTH_ENABLED:
    # django-allauth
    # ------------------------------------------------------------------------------
    ACCOUNT_ALLOW_REGISTRATION = env.bool("DJANGO_ACCOUNT_ALLOW_REGISTRATION", True)
    # https://django-allauth.readthedocs.io/en/latest/configuration.html
    ACCOUNT_AUTHENTICATION_METHOD = "username_email" # pai
    # https://django-allauth.readthedocs.io/en/latest/configuration.html
    ACCOUNT_EMAIL_REQUIRED = True
    # https://django-allauth.readthedocs.io/en/latest/configuration.html
    ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    # https://django-allauth.readthedocs.io/en/latest/configuration.html
    ACCOUNT_ADAPTER = "django_sso_app.backend.adapters.UserAdapter"
    # https://django-allauth.readthedocs.io/en/latest/configuration.html
    #SOCIALACCOUNT_ADAPTER = "django_sso_app.backend.adapters.SocialAccountAdapter"
    # pai
    ACCOUNT_CONFIRM_EMAIL_ON_GET = True
    ACCOUNT_USERNAME_REQUIRED = True
    ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False
    ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = LOGIN_URL
    ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = LOGIN_URL
    ACCOUNT_SESSION_REMEMBER = False

    ACCOUNT_FORMS = {
        'signup': 'django_sso_app.backend.forms.SignupForm'
    }
# Your stuff...

# pai

REPOSITORY_REV = env("REPOSITORY_REV", default=None)

FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

ENABLE_HTTPS = env.bool("ENABLE_HTTPS", False)

ACCOUNT_DEFAULT_HTTP_PROTOCOL = env("ACCOUNT_DEFAULT_HTTP_PROTOCOL", default="https" if ENABLE_HTTPS else "http")
APPEND_SLASH = True

APP_DOMAIN = env("APP_DOMAIN", default="localhost:8000")
APP_DOMAINS = env.list("APP_DOMAINS", default=[APP_DOMAIN, ])
APP_URL = ACCOUNT_DEFAULT_HTTP_PROTOCOL + '://' + APP_DOMAIN

COOKIE_DOMAIN = env("COOKIE_DOMAIN", default=APP_DOMAIN)

# cors
if DEBUG:
    CORS_ORIGIN_ALLOW_ALL = True
else:
    # https://github.com/ottoyiu/django-cors-headers
    # CORS headers defaults to 'accounts.example.com'
    _CORS_ORIGINS = env("CORS_ORIGINS", default='{0}://{1}'.format(ACCOUNT_DEFAULT_HTTP_PROTOCOL, COOKIE_DOMAIN))
    CORS_ORIGIN_WHITELIST = list(map(lambda x: '{}'.format(x.replace(' ', '')), _CORS_ORIGINS.split(',')))
    #CORS_ORIGIN_WHITELIST = _CORS_ORIGINS.split(',')
    CORS_ALLOW_CREDENTIALS = True

# csrf
# https://docs.djangoproject.com/en/2.0/ref/settings/#csrf-trusted-origins

if DEBUG:
    CSRF_COOKIE_DOMAIN = None
    CORS_ORIGIN_ALLOW_ALL = True
    CSRF_TRUSTED_ORIGINS = []
else:
    CSRF_COOKIE_DOMAIN = APP_DOMAIN
    CSRF_TRUSTED_ORIGINS = ['.{0}'.format(COOKIE_DOMAIN)]

if DJANGO_SSO_APP_ENABLED:
    # django-sso-app

    DJANGO_SSO_USER_PROFILE_MODEL = 'django_sso_app.core.apps.profiles.models.Profile'

    AUTHENTICATION_BACKENDS = AUTHENTICATION_BACKENDS + [
        'django_sso_app.app.backends.DjangoSsoAppBackend',
    ]

    _LOGGING_LEVEL = 'INFO'
    if DEBUG:
        _LOGGING_LEVEL = 'DEBUG'

    LOGGING['django_sso_app'] = {
        'handlers': ['console'],
        'propagate': True,
        'level': _LOGGING_LEVEL
    }


# djangorestframework

DRF_DEFAULT_AUTHENTICATION_CLASSES = [
    'rest_framework.authentication.SessionAuthentication',
    'rest_framework.authentication.TokenAuthentication'
]

if DJANGO_SSO_BACKEND_ENABLED:
    DRF_DEFAULT_AUTHENTICATION_CLASSES = [
        'django_sso_app.core.apps.users.authentication.UsersAuthentication',
    ] + DRF_DEFAULT_AUTHENTICATION_CLASSES

if DJANGO_SSO_APP_ENABLED:
    DRF_DEFAULT_AUTHENTICATION_CLASSES += [
        'django_sso_app.app.authentication.DjangoSsoAppAuthentication'
    ]


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


# swagger

SWAGGER_SETTINGS = {
    'LOGIN_URL': '/admin/login/',
    'LOGOUT_URL': '/admin/logout/',
    'SECURITY_DEFINITIONS': {
        'JWT': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Bearer xxx'
        },
        'token': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Token xxx'
        }
    }
}

# ------------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s:%(name)s: %(message)s '
                      '(%(asctime)s; %(filename)s:%(lineno)d)',
            'datefmt': "%Y-%m-%d %H:%M:%S",
        },
    },
    'handlers': {
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'users': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'profiles': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'devices': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'services': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'passepartout': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'api_gateway': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'backend': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'django': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# rest_auth

REST_USE_JWT = True
REST_AUTH_SERIALIZERS = {
    'LOGIN_SERIALIZER': 'django_sso_app.backend.serializers.LoginSerializer',
    'PASSWORD_RESET_SERIALIZER': 'django_sso_app.backend.serializers.PasswordResetSerializer',
    'USER_DETAILS_SERIALIZER' : 'django_sso_app.core.apps.users.serializers.UserSerializer',
}

REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'django_sso_app.backend.serializers.RegisterSerializer',
}

JWT_AUTH = {
    'JWT_AUTH_COOKIE': 'jwt',

    'JWT_PAYLOAD_HANDLER': 'django_sso_app.backend.handlers.jwt_payload_handler',
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_VERIFY': False,
}


print('ROOT_DIR', ROOT_DIR, "INSTALLED_APPS", INSTALLED_APPS)
