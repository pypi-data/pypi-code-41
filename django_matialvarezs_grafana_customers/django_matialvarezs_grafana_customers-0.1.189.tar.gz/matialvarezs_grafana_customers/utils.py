from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.db.models import Q
from ohm2_handlers_light import utils as h_utils
from ohm2_handlers_light.definitions import RunException
from . import models as matialvarezs_grafana_customers_models
from . import errors as matialvarezs_grafana_customers_errors
from . import settings
import os, time, random
from ohm2_handlers_light import utils as ohm2_handlers_light_utils

random_string = "cVXmRyoYIJNTdxWLvIHdKBgLJYykfjhy"



"""
def parse_model_attributes(**kwargs):
	attributes = {}
	
	return attributes

def create_model(**kwargs):

	for key, value in parse_model_attributes(**kwargs).items():
		kwargs[key] = value
	return h_utils.db_create(matialvarezs_grafana_customers_models.Model, **kwargs)

def get_model(**kwargs):
	return h_utils.db_get(matialvarezs_grafana_customers_models.Model, **kwargs)

def get_or_none_model(**kwargs):
	return h_utils.db_get_or_none(matialvarezs_grafana_customers_models.Model, **kwargs)

def filter_model(**kwargs):
	return h_utils.db_filter(matialvarezs_grafana_customers_models.Model, **kwargs)

def q_model(q, **otions):
	return h_utils.db_q(matialvarezs_grafana_customers_models.Model, q)

def delete_model(entry, **options):
	return h_utils.db_delete(entry)

def update_model(entry, **kwargs):
	attributes = {}
	for key, value in parse_model_attributes(**kwargs).items():
		attributes[key] = value
	return h_utils.db_update(entry, **attributes)
"""

def get_or_none_organisation_grafana(**kwargs):
    return ohm2_handlers_light_utils.db_get_or_none(matialvarezs_grafana_customers_models.OrganisationGrafana, **kwargs)


def create_organisation_grafana(**kwargs):
    return ohm2_handlers_light_utils.db_create(matialvarezs_grafana_customers_models.OrganisationGrafana, **kwargs)


def get_or_none_dashboard_grafana(**kwargs):
    return ohm2_handlers_light_utils.db_get_or_none(matialvarezs_grafana_customers_models.DashboardGrafana, **kwargs)


def get_or_none_panel_grafana(**kwargs):
    return ohm2_handlers_light_utils.db_get_or_none(matialvarezs_grafana_customers_models.PanelGrafana, **kwargs)


def get_or_none_dashboard_panel_grafana(**kwargs):
    return ohm2_handlers_light_utils.db_get_or_none(matialvarezs_grafana_customers_models.DashboardPanelsGrafana, **kwargs)


def get_or_none_folder_grafana(**kwargs):
    return ohm2_handlers_light_utils.db_get_or_none(matialvarezs_grafana_customers_models.FolderGrafana, **kwargs)


def get_or_none_rows_dashboard(**kwargs):
    return ohm2_handlers_light_utils.db_get_or_none(matialvarezs_grafana_customers_models.RowsDashboardGrafana, **kwargs)

def create_user_grafana(**kwargs):
    grafana_user = get_or_none_user_grafana(**kwargs)
    if grafana_user is None:
        return ohm2_handlers_light_utils.db_create(matialvarezs_grafana_customers_models.DjangoGrafanaUser, **kwargs)
    return grafana_user
def get_or_none_user_grafana(**kwargs):
    return ohm2_handlers_light_utils.db_get_or_none(matialvarezs_grafana_customers_models.DjangoGrafanaUser, **kwargs)