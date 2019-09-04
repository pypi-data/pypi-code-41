from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.db.models import Q
from ohm2_handlers_light import utils as h_utils
from ohm2_handlers_light.definitions import RunException
from . import models as matialvarezs_node_configurations_models
from . import errors as matialvarezs_node_configurations_errors
from . import settings
import os, time, random


random_string = "nH9atFxHrJXILHuXXUPa9o5kJGT0q0E3"



"""
def parse_model_attributes(**kwargs):
	attributes = {}
	
	return attributes

def create_model(**kwargs):

	for key, value in parse_model_attributes(**kwargs).items():
		kwargs[key] = value
	return h_utils.db_create(matialvarezs_node_configurations_models.Model, **kwargs)

def get_model(**kwargs):
	return h_utils.db_get(matialvarezs_node_configurations_models.Model, **kwargs)

def get_or_none_model(**kwargs):
	return h_utils.db_get_or_none(matialvarezs_node_configurations_models.Model, **kwargs)

def filter_model(**kwargs):
	return h_utils.db_filter(matialvarezs_node_configurations_models.Model, **kwargs)

def q_model(q, **otions):
	return h_utils.db_q(matialvarezs_node_configurations_models.Model, q)

def delete_model(entry, **options):
	return h_utils.db_delete(entry)

def update_model(entry, **kwargs):
	attributes = {}
	for key, value in parse_model_attributes(**kwargs).items():
		attributes[key] = value
	return h_utils.db_update(entry, **attributes)
"""
def get_or_none_configuration(**kwargs):
    return h_utils.db_get_or_none(matialvarezs_node_configurations_models.Configuration, **kwargs)


def create_configuration(**kwargs):
    key = kwargs.get('key')
    config = get_or_none_configuration(key=key)
    if config is None:
        return h_utils.db_create(matialvarezs_node_configurations_models.Configuration, **kwargs)
    return config

def get_identity():
    return h_utils.db_get_or_none(matialvarezs_node_configurations_models.Configuration,key='identity').value

