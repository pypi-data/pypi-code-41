import psu_base as app
from django.contrib.messages import constants as messages

# Version of psu-base plugin
PSU_BASE_VERSION = app.__version__

# PSU Centralized Repository
CENTRALIZED_NONPROD = 'https://content.oit.pdx.edu/nonprod'
CENTRALIZED_PROD = 'https://content.oit.pdx.edu'

# Set Timezone
TIME_ZONE = 'America/Vancouver'

# Message classes
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# Logging Settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': "logs/django",
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'dbfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': "logs/db_backend",
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'logfile'],
            'propagate': True,
            'level': 'WARN',
        },
        'django.db.backends': {
            'handlers': ['dbfile'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'psu': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
        },
    }
}

# SSO SETTINGS
CAS_APPLY_ATTRIBUTES_TO_USER = True
CAS_CREATE_USER = True
CAS_IGNORE_REFERER = True
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_cas_ng.backends.CASBackend',
)

# EMAIL SETTINGS
EMAIL_HOST = 'mailhost.pdx.edu'
EMAIL_PORT = 25
EMAIL_SENDER = 'noreply@pdx.edu'

# Session expiration
SESSION_COOKIE_AGE = 30 * 60  # 30 minutes

# Globally require authentication by default
REQUIRE_LOGIN = True
PSU_PUBLIC_URLS = ['.*/psu/test', '.*/accounts/login']

# Must be overwritten in app_settings
CAS_REDIRECT_URL = '/URL_CONTEXT'
LOGIN_URL = 'cas:login'

# May be overwritten in local_settings:
CAS_SERVER_URL = 'https://sso-stage.oit.pdx.edu/idp/profile/cas/login'
