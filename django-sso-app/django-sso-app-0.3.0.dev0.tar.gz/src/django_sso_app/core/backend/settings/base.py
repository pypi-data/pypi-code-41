import environ

env = environ.Env()

# django-sso
DJANGO_SSO_BACKEND_ENABLED = True
DJANGO_SSO_APP_ENABLED = env.bool('DJANGO_SSO_APP_ENABLED', default=(not DJANGO_SSO_BACKEND_ENABLED))

if DJANGO_SSO_BACKEND_ENABLED:
    from .backend import *

if DJANGO_SSO_APP_ENABLED:
    from .app import *
