from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.db.models import Q
from ohm2_handlers_light import utils as h_utils
from ohm2_handlers_light.definitions import RunException
from . import models as matialvarezs_charge_controller_models
from . import errors as matialvarezs_charge_controller_errors
from . import settings
import os, time, random


random_string = "NzmXq9jLxGJGyDFHrj4F07d97F284t7j"



"""
def parse_model_attributes(**kwargs):
	attributes = {}
	
	return attributes

def create_model(**kwargs):

	for key, value in parse_model_attributes(**kwargs).items():
		kwargs[key] = value
	return h_utils.db_create(matialvarezs_charge_controller_models.Model, **kwargs)

def get_model(**kwargs):
	return h_utils.db_get(matialvarezs_charge_controller_models.Model, **kwargs)

def get_or_none_model(**kwargs):
	return h_utils.db_get_or_none(matialvarezs_charge_controller_models.Model, **kwargs)

def filter_model(**kwargs):
	return h_utils.db_filter(matialvarezs_charge_controller_models.Model, **kwargs)

def q_model(q, **otions):
	return h_utils.db_q(matialvarezs_charge_controller_models.Model, q)

def delete_model(entry, **options):
	return h_utils.db_delete(entry)

def update_model(entry, **kwargs):
	attributes = {}
	for key, value in parse_model_attributes(**kwargs).items():
		attributes[key] = value
	return h_utils.db_update(entry, **attributes)
"""

def create_local_data_backup(**kwargs):
    return h_utils.db_create(matialvarezs_charge_controller_models.LocalDataBackup, **kwargs)


def filter_local_data_backup(**kwargs):
    return h_utils.db_filter(matialvarezs_charge_controller_models.LocalDataBackup, **kwargs)

def filter_registers_data(**kwargs):
    return h_utils.db_filter(matialvarezs_charge_controller_models.RegistersData, **kwargs)

def create_registers_data(**kwargs):
    return h_utils.db_create(matialvarezs_charge_controller_models.RegistersData, **kwargs)