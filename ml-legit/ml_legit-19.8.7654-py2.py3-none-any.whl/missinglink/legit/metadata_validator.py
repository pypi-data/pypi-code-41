# -*- coding: utf-8 -*-
import six
import collections
import re


class MetadataValidator(object):

    DUPLICATE_KEY_ERROR = 'More than one field with same name in different casing is not allowed: "{}"'
    WHITESPACE_ERROR = 'Whitespaces in field names are not allowed: "{}"'
    INCONSISTENT_SCHEMA_ERROR = 'Inconsistent field type. Please make sure field type (primitive, array or dictionary) is consistent across all files. Field: {}'

    def __init__(self, data, metadata_schema):
        self._data = data
        self._metadata_schema = metadata_schema
        self._errors = []
        self._lower_keys = collections.defaultdict(list)

    def _validate_duplicate_keys(self):
        for key in self._data.keys():
            if isinstance(key, six.string_types):
                self._lower_keys[key.lower()].append(key)

        for lower_key, keys in self._lower_keys.items():
            if len(keys) > 1:
                error = self.DUPLICATE_KEY_ERROR.format('","'.join(sorted(keys)))
                self._errors.append(error)

    def _validate_space_in_keys(self):
        pattern = re.compile('\\s')
        for key in self._data.keys():
            if pattern.search(key):
                error = self.WHITESPACE_ERROR.format(key)
                self._errors.append(error)

    def _validate_schema_consistency(self):
        for key in self._data.keys():
            if not self._is_schema_consistent(key):
                key_name = key.replace('_json', '') if '_json' in key else key
                error = self.INCONSISTENT_SCHEMA_ERROR.format(key_name)
                self._errors.append(error)

    def _is_schema_consistent(self, key):
        """
        Schema is consistent as long as it refers to a key only once
        primitives are registered as the key name
        in complex objects (lists/dicts) the key is suffixed with '_json'
        if both variants appear in the schema it is inconsistent

        Args:
            key: (str)

        Returns: (bool)
        """
        other_variant_key = key.replace('_json', '') if '_json' in key else '{}_json'.format(key)
        return other_variant_key not in self._metadata_schema

    def get_validation_errors(self):
        self._validate_duplicate_keys()
        self._validate_space_in_keys()
        self._validate_schema_consistency()
        return self._errors
