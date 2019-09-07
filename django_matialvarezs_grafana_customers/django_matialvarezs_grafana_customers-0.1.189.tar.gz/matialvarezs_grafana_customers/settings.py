from django.conf import settings
from django.utils.translation import ugettext as _
import os


DEBUG = getattr(settings, 'DEBUG')
BASE_DIR = getattr(settings, 'BASE_DIR')
STRING_SINGLE = getattr(settings, 'STRING_SINGLE')
STRING_SHORT = getattr(settings, 'STRING_SHORT')
STRING_MEDIUM = getattr(settings, 'STRING_MEDIUM')
STRING_NORMAL = getattr(settings, 'STRING_NORMAL')
STRING_LONG = getattr(settings, 'STRING_LONG')
STRING_DOUBLE = getattr(settings, 'STRING_DOUBLE')
HOST = getattr(settings, 'HOST')
SUBDOMAINS = getattr(settings, 'SUBDOMAINS')
PROTOCOL = getattr(settings, 'PROTOCOL')
HOSTNAME = getattr(settings, 'HOSTNAME')
WEBSITE_URL = getattr(settings, 'WEBSITE_URL')
STATIC_URL = getattr(settings, 'STATIC_URL')
STATIC_ROOT = getattr(settings, 'STATIC_ROOT')
MEDIA_URL = getattr(settings, 'MEDIA_URL')
MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
ADMINS = getattr(settings, 'ADMINS', [])

APP = 'MATIALVAREZS_GRAFANA_CUSTOMERS_'

VARIABLE = getattr(settings, APP + 'VARIABLE', None)

GRAFANA_API_KEY = getattr(settings,'GRAFANA_API_KEY','')
GRAFANA_API_HEADERS = getattr(settings,'GRAFANA_API_HEADERS',{})
GRAFANA_API_BASE_URL = getattr(settings,'GRAFANA_API_BASE_URL','')
DATASOURCE_NAME = getattr(settings,'GRAFANA_DATASOURCE_NAME','')
DATABASE_NAME = getattr(settings,'DATABASE_NAME','')
DATABASE_USER = getattr(settings,'DATABASE_USER','')
DATABASE_PASSWORD = getattr(settings,'DATABASE_PASSWORD','')
DATABASE_HOST = getattr(settings,'DATABASE_HOST','')
DATABASE_PORT = getattr(settings,'DATABASE_PORT','')


INFLUX_DATABASE = getattr(settings, 'INFLUX_DATABASE','')
INFLUX_USER = getattr(settings, 'INFLUX_USER','')
INFLUX_PASSWORD = getattr(settings, 'INFLUX_PASSWORD','')
INFLUX_HOST = getattr(settings, 'INFLUX_HOST','')
INFLUX_PORT = getattr(settings, 'INFLUX_PORT','')
INFLUX_URL = getattr(settings, 'INFLUX_URL','')