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

APP = 'MATIALVAREZS_CHARGE_CONTROLLER_'
MODBUS_CLIENT_TYPE = getattr(settings,APP+'MODBUS_CLIENT_TYPE','TCP')
MODBUS_CLIENT_SERIAL_PORT = getattr(settings,APP+'MODBUS_CLIENT_SERIAL_PORT','USB0')

VARIABLE = getattr(settings, APP + 'VARIABLE', None)

SCRIPTS_PATH = getattr(settings, 'SCRIPTS_PATH')
CRON_JOB_LOGS_PATH = getattr(settings, 'CRON_JOB_LOGS_PATH')
CRONTAB_USER = getattr(settings,'CRONTAB_USER')

PRODUCTION_CONFIG = getattr(settings,'PRODUCTION_CONFIG')
APP = 'NETWORK_'
SERVER_PROTOCOL = getattr(settings, APP + 'SISNBYTED_CENTRAL_SERVER_PROTOCOL','')
IP_CENTRAL_SERVER = getattr(settings, APP + 'SISNBYTED_CENTRAL_SERVER_IP','')
SERVER_API_PORT = getattr(settings, APP + 'SISNBYTED_CENTRAL_SERVER_API_PORT','')

IP_API_CENTRAL_SERVER = SERVER_PROTOCOL + "://" + IP_CENTRAL_SERVER + ":" + SERVER_API_PORT
SISNBYTED_REQUEST_HEADERS = getattr(settings,'SISNBYTED_REQUEST_HEADERS',{})

MATIALVAREZS_CHARGE_CONTROLLER_CREATE_DATA_CHARGE_CONTROLLER_URL = IP_API_CENTRAL_SERVER+'/charge_controller/api/v1/create_data_charge_controller/'
