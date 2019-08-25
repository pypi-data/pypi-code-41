#!python

import logging
import json
import re


# Error class used for all exceptions from the package
class SchemaCheckError(BaseException):
  
  def __init__(self, msg):
    """Initialise with a given message."""
    super().__init__(msg)
    self.msg = msg


class Schema:

  OBJECT_TYPE  = type(json.loads('{}'))
  ARRAY_TYPE   = type(json.loads('[]'))
  STRING_TYPE  = type(json.loads('""'))
  INT_TYPE     = type(json.loads('0'))
  FLOAT_TYPE   = type(json.loads('0.0'))
  BOOLEAN_TYPE = type(json.loads('true'))
  NULL_TYPE    = type(json.loads('null'))

  def __init__(self, path):
    """Read the JSON file with the given path as the schema."""
    self.__logger = logging.getLogger(__name__)
    try:
      with open(path, 'r') as f:
        self._schema = json.load(f)
    except IOError:
      self.__logger.error('Error opening JSON schema file')
      raise SchemaCheckError('Error opening JSON schema file')
    except json.JSONDecodeError:
      self.__logger.error('Error decoding JSON schema')
      raise SchemaCheckError('Error decoding JSON schema')
    except:
      self.__logger.error('An unknown error occurred. Please contact the package maintainer')
      raise SchemaCheckError('An Unknown error occurred. Please contact the package maintainer')

  def check(self, unchecked):
    """Throw a SchemaCheckError if the given unchecked JSON data does not match the schema."""
    self.__check(self._schema, unchecked)

  def __check(self, checked, unchecked):
    """Throw a SchemaCheckError if the given unchecked JSON data does not match the given checked schema"""
    if (type(checked) == Schema.OBJECT_TYPE):
      self.__check_object(checked, unchecked)
    elif (type(checked) == Schema.ARRAY_TYPE):
      self.__check_array(checked, unchecked)
    elif (type(checked) == Schema.STRING_TYPE):
      self.__check_string(checked, unchecked)
    else:
      self.__logger.error('Unexpected type')
      raise SchemaCheckError('Unexpected type')

  def __check_string(self, checked, unchecked):
    """Throw a SchemaCheckError if the unchecked JSON data does not match the JEX"""
    OBJECT_WILDCARD  = '$object'
    ARRAY_WILDCARD   = '$array'
    STRING_WILDCARD  = '$string'
    NUMBER_WILDCARD  = '$number'
    BOOLEAN_WILDCARD = '$boolean'
    NULL_WILDCARD    = '$null'
    if (checked == OBJECT_WILDCARD):
      if (type(unchecked) != Schema.OBJECT_TYPE):
        self.__logger.error('Objected expected')
        raise SchemaCheckError('Object expected')
      return
    elif (checked == ARRAY_WILDCARD):
      if (type(unchecked) != Schema.ARRAY_TYPE):
        self.__logger.error('Array expected')
        raise SchemaCheckError('Array expected')
      return
    elif (checked == STRING_WILDCARD):
      if (type(unchecked) != Schema.STRING_TYPE):
        self.__logger.error('String expected')
        raise SchemaCheckError('String expected')
      return
    elif (checked == NUMBER_WILDCARD):
      if (not type(unchecked) in (Schema.INT_TYPE, Schema.FLOAT_TYPE)):
        self.__logger.error('Number expected')
        raise SchemaCheckError('Number expected')
      return
    elif (checked == BOOLEAN_WILDCARD):
      if (type(unchecked) != Schema.BOOLEAN_TYPE):
        self.__logger.error('Boolean expected')
        raise SchemaCheckError('Boolean expected')
      return
    elif (checked == NULL_WILDCARD):
      if (type(unchecked) != Schema.NULL_TYPE):
        self.__logger.error('Null expected')
        raise SchemaCheckError('Null expected')
      return
    else:
      try:
        checked_json = json.loads(checked)
        self.__check(checked_json, unchecked)
      except json.JSONDecodeError:
        self.__logger.error('Error decoding JSON schema')
        raise SchemaCheckError('Error decoding JSON schema')

  def __check_object(self, checked, unchecked):
    """Throw a SchemaCheckError if the unchecked JSON data does not match the checked JSON object"""
    if (type(unchecked) != Schema.OBJECT_TYPE):
      self.__logger.error('Object expected')
      raise SchemaCheckError('Object expected')
    if (checked.keys() != unchecked.keys()):
      self.__logger.error('Fields of object do not matched expected fields')
      raise SchemaCheckError('Fields do not match')
    for field in checked:
      try:
        self.__check(checked[field], unchecked[field])
      except SchemaCheckError:
        self.__logger.error(f'Check failed for some field {field}')
        raise

  def __check_array(self, checked, unchecked):
    """Throw a SchemaCheckError if the unchecked JSON data does not match the checked JSON array"""
    if (type(unchecked) != Schema.ARRAY_TYPE):
      self.__logger.error('Array Expected')
    for item in unchecked:
      item_checked = False
      for item_scheme in checked:
        try:
          self.__check_string(item_scheme, item)
          item_checked = True
        except SchemaCheckError:
          continue
      if (not item_checked):
        self.__logger.error('Array item does not fit any item schema')
        raise SchemaCheckError('Array item does not fit any item schema')
