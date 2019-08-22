''' String FieldValue Validators '''

import re
import string

from .combinations import validate_all, validate_any
from .common import failure


ALPHANUM = string.digits + string.ascii_letters + "_"


def length_validator(min_len=None, max_len=None):
    ''' 
    Validate String Length

    If min or max (or both) are specified, length must comply

    '''

    def validator(field_value):
        ''' Validator '''
        value = field_value.get()
        value_len = len(value)
        if min_len is not None and value_len < min_len:
            return failure(field_value,
                           "Value too short. Must be at least %s characters, got %s (%s)",
                           min_len, value_len, value)
        if max_len is not None and len(value) > max_len:
            return failure(field_value,
                           "Value too long. Must be at most %s characters, got %s (%s)",
                           max_len, value_len, value)
        return True

    return validator


def charset_validator(charset=None, start_with=None):
    ''' Validate against charsets.
        if charset is set, the value must consist of only characters in that charset
        if start_with is specified, first character must be in that charset
    '''
    full_charset = set(charset) if charset is not None else None
    start_charset = set(start_with) if start_with is not None else None

    def validator(field_value):
        ''' Validator '''
        value = field_value.get()
        if value:
            if start_charset and value[0] not in start_charset:
                return failure(field_value, "First character is invalid - '%s'", value[0])
            if full_charset and not full_charset.issuperset(set(value)):
                return failure(field_value, "Invalid characters in field - value '%s'", value)

        return True
    return validator


def regex_validator(pattern=None):
    ''' Validate against regex pattern.
    '''
    regex = re.compile(pattern if pattern else r".*")

    def validator(field_value):
        ''' Validator '''
        value = field_value.get()
        if value is not None:
            if not regex.match(value):
                return failure(field_value, "Value '%s' does not match the expected pattern",
                               value)
            return True
        return False
    return validator


def choice_validator(one_of=None, not_one_of=None):
    ''' Validate against lists.
        if one_of is specified, value must exactly match one of the values
        if not_one_of is specified, value must NOT match one of the values
    '''

    def validator(field_value):
        ''' Validator '''
        value = field_value.get()
        if one_of and value not in one_of:
            return failure(field_value, "Value '%s' is not in list of allowed values ('%s')",
                           value, "', '".join(one_of))
        if not_one_of and value in not_one_of:
            return failure(field_value, "Value '%s' is on list of disallowed values ('%s')",
                           value, "', '".join(not_one_of))
        return True

    return validator


def string_validator(min_len=None, max_len=None, charset=None, start_with=None,
                     one_of=None, not_one_of=None, allow_blank=None, alt_choices=None):
    main_list = []
    alt_validator = None
    if min_len is not None or max_len is not None:
        main_list.append(length_validator(min_len, max_len))
    if one_of is not None or not_one_of is not None:
        main_list.append(choice_validator(one_of, not_one_of))
    if charset is not None or start_with is not None:
        main_list.append(charset_validator(charset, start_with))
    if allow_blank:
        if alt_choices is None:
            alt_choices = []
        if '' not in alt_choices:
            alt_choices.append('')
    if alt_choices:
        alt_validator = choice_validator(one_of=alt_choices)
    main_validator = validate_all(*main_list) if main_list else None
    if not main_validator and not alt_validator:
        return validate_all()
    if not main_validator and alt_validator:
        return alt_validator
    if main_validator and not alt_validator:
        return main_validator

    return validate_any(alt_validator, main_validator)
