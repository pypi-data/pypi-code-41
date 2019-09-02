from django.conf import settings

GRAFANA_API_KEY = getattr(settings,'GRAFANA_API_KEY')
GRAFANA_API_HEADERS = getattr(settings,'GRAFANA_API_HEADERS')
GRAFANA_API_BASE_URL = getattr(settings,'GRAFANA_API_BASE_URL')
DATASOURCE_NAME = getattr(settings,'GRAFANA_DATASOURCE_NAME')
DATABASE_NAME = getattr(settings,'DATABASE_NAME')
DATABASE_USER = getattr(settings,'DATABASE_USER')
DATABASE_PASSWORD = getattr(settings,'DATABASE_PASSWORD')
DATABASE_HOST = getattr(settings,'DATABASE_HOST')
DATABASE_PORT = getattr(settings,'DATABASE_PORT')


INFLUX_DATABASE = getattr(settings, 'INFLUX_DATABASE')
INFLUX_USER = getattr(settings, 'INFLUX_USER')
INFLUX_PASSWORD = getattr(settings, 'INFLUX_PASSWORD')
INFLUX_HOST = getattr(settings, 'INFLUX_HOST')
INFLUX_PORT = getattr(settings, 'INFLUX_PORT')
INFLUX_URL = getattr(settings, 'INFLUX_URL')