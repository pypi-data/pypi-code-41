"""
Generic script for CSV to OCL-formatted JSON conversion.
Converting from CSV to JSON is a commonly used function and this script
provides a generic method for defining CSV files.

Columns:
[Optional] (owner_type, owner_id, source) OR (source_url) OR (set environment variable)
concept_id

mapping_01_id


TODO:
- Implement OCL core ability to manually define mapping ID
- 
"""
import ocldev.oclconstants
import csv
import json


class OclCsvConversionDefinitionSet:
    """ A set of CSV conversion definitions """

    def to_json(self):
    	pass

    def load_from_json(self):
    	pass

    def add(self, csv_def):
    	pass

    def get(self):
    	pass

    # iterator
    #


class OclCsvConversionDefinition:
    """ Defines a single CSV conversion definition """

	defaults = {
		"name_01_type": "Fully Specified"
	}

	csv_definition = {

	}

    def __init__(self, definition_name="", is_active=True, resource_type=oclconstants.OclConstants.RESOURCE_TYPE_CONCEPT,
    			 id_column="", skip_if_empty_column="", skip_handler="", core_fields=None, names=None, descriptions=None,
    			 extras=None):
    	pass




class OclCsvImporter:
    """ Class to import a CSV file into OCL """
	pass


class OclCsvConverter:
	""" Class to convert a CSV file into OCL-formatted JSON """
	pass

